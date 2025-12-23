
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv(override=True)

def check_count():
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
    
    supabase = create_client(url, key)
    
    try:
        # Get count (exact count might be slow on big tables, but head count is fine)
        res = supabase.table("message_embeddings").select("id", count="exact").limit(1).execute()
        count = res.count
        print(f"Total Embeddings stored: {count}")
        
        # Check last ID
        res_last = supabase.table("message_embeddings").select("original_id").order("original_id", desc=True).limit(1).execute()
        if res_last.data:
            print(f"Last Processed Message ID: {res_last.data[0]['original_id']}")
            
    except Exception as e:
        print(f"Error checking count: {e}")

if __name__ == "__main__":
    check_count()
