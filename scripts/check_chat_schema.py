
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Setup path like metrics_extractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv()

def check_chat_schema():
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
    client = create_client(url, key)
    
    print("Fetching n8n_chat_histories sample...")
    res = client.table("n8n_chat_histories").select("*").limit(1).execute()
    if res.data:
        print(f"Columns: {list(res.data[0].keys())}")
        print(f"Sample: {res.data[0]}")
    else:
        print("Table empty")

if __name__ == "__main__":
    check_chat_schema()
