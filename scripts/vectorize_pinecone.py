
import os
import sys
import time
from dotenv import load_dotenv
from supabase import create_client
from openai import AzureOpenAI
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv(override=True)

# Configuration
BATCH_SIZE = 100
MODEL_DEPLOYMENT = os.getenv("MODEL_NAME", "text-embedding-ada-002")
PINECONE_INDEX_NAME = "belevita-chat"

def setup_services():
    # Supabase (source data)
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
    supabase = create_client(url, key)

    # Azure OpenAI
    azure_api_key = os.getenv("AZURE_API_KEY")
    api_version = os.getenv("MODEL_VERSION", "2023-05-15")
    if not azure_api_key:
        raise ValueError("AZURE_API_KEY not found")
    azure_client = AzureOpenAI(
        api_key=azure_api_key,
        api_version=api_version,
        azure_endpoint="https://opus-brain-resource.cognitiveservices.azure.com/"
    )

    # Pinecone
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY not found")
    
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Check if index exists, create if not
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        print(f"Creating index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # text-embedding-ada-002
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        # Wait for index to be ready
        time.sleep(10)
    
    index = pc.Index(PINECONE_INDEX_NAME)
    
    return supabase, azure_client, index

def vectorize_to_pinecone():
    supabase, azure_client, pinecone_index = setup_services()
    
    # Get index stats to find where we left off
    stats = pinecone_index.describe_index_stats()
    total_vectors = stats.total_vector_count
    print(f"Current vectors in Pinecone: {total_vectors}")
    
    # We'll track progress by keeping a local file with the last processed ID
    progress_file = "pinecone_progress.txt"
    last_id = 0
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            last_id = int(f.read().strip())
    
    print(f"Starting from ID: {last_id}")
    print(f"Using Azure Deployment: {MODEL_DEPLOYMENT}")
    
    processed_count = 0
    
    while True:
        try:
            res = supabase.table("n8n_chat_histories") \
                .select("id, session_id, message") \
                .gt("id", last_id) \
                .order("id") \
                .limit(BATCH_SIZE) \
                .execute()
            
            rows = res.data
            if not rows:
                print("No more messages to process.")
                break
                
            valid_texts = []
            records_to_embed = []
            
            for row in rows:
                msg_data = row.get("message", {})
                content = ""
                msg_type = ""
                
                if isinstance(msg_data, dict):
                    content = msg_data.get("content", "")
                    msg_type = msg_data.get("type", "unknown")
                elif isinstance(msg_data, str):
                    content = msg_data
                    msg_type = "unknown"
                
                # Only embed meaningful text
                if content and isinstance(content, str) and len(content.strip()) > 3:
                    clean_content = content.replace("\n", " ")[:8000]  # Limit content length
                    valid_texts.append(clean_content)
                    records_to_embed.append({
                        "id": str(row["id"]),
                        "session_id": row["session_id"],
                        "content": content[:1000],  # Store truncated for metadata
                        "type": msg_type
                    })
                
                last_id = row["id"]
            
            if not valid_texts:
                print(f"Skipping batch... cursor at {last_id}")
                # Save progress
                with open(progress_file, 'w') as f:
                    f.write(str(last_id))
                continue

            # Generate Embeddings
            try:
                response = azure_client.embeddings.create(
                    input=valid_texts,
                    model=MODEL_DEPLOYMENT
                )
                
                vectors = [item.embedding for item in response.data]
                
                # Prepare upsert for Pinecone
                vectors_to_upsert = []
                for i, record in enumerate(records_to_embed):
                    vectors_to_upsert.append({
                        "id": record["id"],
                        "values": vectors[i],
                        "metadata": {
                            "session_id": record["session_id"],
                            "content": record["content"],
                            "type": record["type"]
                        }
                    })
                
                # Upsert to Pinecone
                pinecone_index.upsert(vectors=vectors_to_upsert)
                processed_count += len(vectors_to_upsert)
                print(f"Processed {len(vectors_to_upsert)} items. Total: {processed_count}. Last ID: {last_id}")
                
                # Save progress
                with open(progress_file, 'w') as f:
                    f.write(str(last_id))
                
            except Exception as e:
                print(f"Error generating/storing embeddings: {e}")
                time.sleep(5)
                
        except Exception as e:
            print(f"Critical Error in loop: {e}")
            break
    
    print(f"\n=== COMPLETE ===")
    print(f"Total processed: {processed_count}")

if __name__ == "__main__":
    vectorize_to_pinecone()
