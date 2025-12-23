
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Setup path like metrics_extractor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_PROJECT_REF

load_dotenv()

def verify():
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLIC_KEY")
    url = os.getenv("SUPABASE_URL")
    
    if not url and SUPABASE_PROJECT_REF:
        url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
        
    print(f"URL: {url}")
    print(f"Key present: {bool(key)}")
    
    try:
        client = create_client(url, key)
        
        print("Checking for leads table...")
        res_leads = client.table("leads").select("*").limit(1).execute()
        if res_leads.data:
            print(f"Leads Columns: {list(res_leads.data[0].keys())}")
            print(f"Sample Lead: {res_leads.data[0]}")
        else:
            print("Leads table is empty or does not exist.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
