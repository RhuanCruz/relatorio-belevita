
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add parent directory to path
sys.path.append(os.getcwd())

load_dotenv()

def check_schema():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    if not supabase_url or not supabase_key:
        print("Missing credentials")
        return

    client = create_client(supabase_url, supabase_key)

    print("--- agent_sessions ---")
    try:
        res = client.table("agent_sessions").select("*").limit(1).execute()
        if res.data:
            print(res.data[0].keys())
            print("Sample ID:", res.data[0].get('id'))
            print("Sample session_id:", res.data[0].get('session_id'))
        else:
            print("No data")
    except Exception as e:
        print(e)
        
    print("\n--- n8n_chat_histories ---")
    try:
        res = client.table("n8n_chat_histories").select("*").limit(1).execute()
        if res.data:
            print(res.data[0].keys())
            print("Sample session_id:", res.data[0].get('session_id'))
        else:
            print("No data")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_schema()
