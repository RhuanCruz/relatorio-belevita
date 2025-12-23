
import os
import sys
import time
from dotenv import load_dotenv
from supabase import create_client
from openai import AzureOpenAI
from tqdm import tqdm

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv(override=True)

# Configuration
BATCH_SIZE = 100  # Azure usually supports larger batches, but sticking to 100 for safety
MODEL_DEPLOYMENT = os.getenv("MODEL_NAME", "text-embedding-ada-002")

def setup_services():
    # Supabase
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
    
    supabase = create_client(url, key)

    # Azure OpenAI
    # Parse base URL from full endpoint or use env var
    full_endpoint = os.getenv("AZURE_ENDPOINT_MODEL")
    api_key = os.getenv("AZURE_API_KEY")
    api_version = os.getenv("MODEL_VERSION", "2023-05-15")
    
    if not api_key:
        raise ValueError("AZURE_API_KEY not found")

    base_url = "https://opus-brain-resource.cognitiveservices.azure.com/"
    if full_endpoint and "opus-brain-resource" in full_endpoint:
        base_url = "https://opus-brain-resource.cognitiveservices.azure.com/"
    
    azure_client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=base_url
    )
    
    return supabase, azure_client

def get_last_processed_id(supabase):
    try:
        res = supabase.table("message_embeddings").select("original_id").order("original_id", desc=True).limit(1).execute()
        if res.data:
            return res.data[0]['original_id']
    except Exception as e:
        print(f"Error checking last id (table might be empty or missing): {e}")
    return 0

def vectorize_chats():
    supabase, azure_client = setup_services()
    last_id = get_last_processed_id(supabase)
    print(f"Starting from ID: {last_id}")
    print(f"Using Azure Deployment: {MODEL_DEPLOYMENT}")
    
    while True:
        # Fetch batch of messages
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
                
                if isinstance(msg_data, dict):
                    content = msg_data.get("content", "")
                elif isinstance(msg_data, str):
                    content = msg_data
                
                # Only embed meaningful text
                if content and isinstance(content, str) and len(content.strip()) > 3:
                    # Sanitize content for embedding
                    clean_content = content.replace("\n", " ")
                    valid_texts.append(clean_content)
                    records_to_embed.append({
                        "original_id": row["id"],
                        "session_id": row["session_id"],
                        "content": content
                    })
                
                last_id = row["id"]
            
            if not valid_texts:
                print(f"Skipping batch... cursor at {last_id}")
                continue

            # Generate Embeddings
            try:
                response = azure_client.embeddings.create(
                    input=valid_texts,
                    model=MODEL_DEPLOYMENT
                )
                
                # Extract embeddings
                vectors = [item.embedding for item in response.data]
                
                # Prepare Upsert
                data_to_insert = []
                for i, record in enumerate(records_to_embed):
                    data_to_insert.append({
                        "original_id": record["original_id"],
                        "session_id": record["session_id"],
                        "content": record["content"],
                        "embedding": vectors[i]
                    })
                
                # Insert into Supabase
                supabase.table("message_embeddings").insert(data_to_insert).execute()
                print(f"Processed {len(data_to_insert)} items. Last ID: {last_id}")
                
            except Exception as e:
                print(f"Error generating/storing embeddings: {e}")
                time.sleep(5)
                
        except Exception as e:
            print(f"Critical Error in loop: {e}")
            break

if __name__ == "__main__":
    vectorize_chats()
