
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.getcwd())
load_dotenv()

def debug_ids():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    
    if not supabase_url or not supabase_key:
        print("Missing credentials")
        return

    client = create_client(supabase_url, supabase_key)

    print("Fetching sample chat histories...")
    chat_res = client.table("n8n_chat_histories").select("session_id").limit(100).execute()
    chat_ids = {r['session_id'] for r in chat_res.data if r.get('session_id')}
    print(f"Found {len(chat_ids)} distinct chat session IDs. Samples: {list(chat_ids)[:3]}")

    print("\nFetching sample agent sessions...")
    agent_res = client.table("agent_sessions").select("session_id").limit(100).execute()
    agent_ids = {r['session_id'] for r in agent_res.data if r.get('session_id')}
    print(f"Found {len(agent_ids)} distinct agent session IDs. Samples: {list(agent_ids)[:3]}")

    overlap = chat_ids.intersection(agent_ids)
    print(f"\nOverlap count in this sample: {len(overlap)}")
    
    if not overlap:
        print("WARNING: No overlap found in small sample. Formats might differ.")

if __name__ == "__main__":
    debug_ids()
