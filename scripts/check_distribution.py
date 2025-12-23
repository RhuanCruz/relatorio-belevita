
import os
import sys
from collections import Counter
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv()

def check_distribution():
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
        
    client = create_client(url, key)
    
    print("Fetching agent_sessions status distribution...")
    # Fetch all status (up to 40k, do in batches or assume sample represents distribution)
    # Just fetching 5000 sample
    res = client.table("agent_sessions").select("status, analyse_sentimental").limit(5000).execute()
    
    statuses = [r.get('status') for r in res.data]
    sentiments = [r.get('analyse_sentimental') for r in res.data]
    
    print(f"Status Distribution (Sample 5000): {Counter(statuses)}")
    print(f"Sentiment Distribution (Sample 5000): {Counter(sentiments)}")
    
    # Check if empty sentiment correlates with 'empty' sessions
    empty_sentiment_count = sum(1 for s in sentiments if not s)
    print(f"Empty Sentiment Count: {empty_sentiment_count}")

if __name__ == "__main__":
    check_distribution()
