
import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone

# Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(override=True)

# Configuration
MODEL_DEPLOYMENT = os.getenv("MODEL_NAME", "text-embedding-ada-002")
PINECONE_INDEX_NAME = "belevita-chat"

def setup():
    # Azure OpenAI
    azure_client = AzureOpenAI(
        api_key=os.getenv("AZURE_API_KEY"),
        api_version=os.getenv("MODEL_VERSION", "2023-05-15"),
        azure_endpoint="https://opus-brain-resource.cognitiveservices.azure.com/"
    )
    
    # Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(PINECONE_INDEX_NAME)
    
    return azure_client, index

def search(azure_client, index, query, top_k=10):
    print(f"\n{'='*60}")
    print(f"🔍 Buscando: '{query}'")
    print(f"{'='*60}")
    
    # Generate embedding for query
    response = azure_client.embeddings.create(
        input=[query],
        model=MODEL_DEPLOYMENT
    )
    query_embedding = response.data[0].embedding
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    print(f"\n📊 Encontrados: {len(results.matches)} resultados")
    print(f"{'='*60}\n")
    
    for i, match in enumerate(results.matches):
        score = match.score
        metadata = match.metadata
        content = metadata.get('content', 'N/A')
        session_id = metadata.get('session_id', 'N/A')
        msg_type = metadata.get('type', 'N/A')
        
        print(f"[{i+1}] Score: {score:.4f} | Tipo: {msg_type} | Session: {session_id[:15]}...")
        print(f"    Conteúdo: {content[:200]}...")
        print()
    
    return results

def main():
    azure_client, index = setup()
    
    # Get index stats
    stats = index.describe_index_stats()
    print(f"\n📈 Total de vetores no Pinecone: {stats.total_vector_count}")
    
    # Test queries
    queries = [
        "cliente insatisfeito reclamando",
        "problema com entrega atrasada",
        "quero cancelar meu pedido",
        "produto veio com defeito",
        "péssimo atendimento nunca mais compro",
        "onde está meu pedido não chegou",
        "quero falar com atendente humano",
        "muito obrigada excelente atendimento"
    ]
    
    for query in queries:
        search(azure_client, index, query, top_k=5)
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    main()
