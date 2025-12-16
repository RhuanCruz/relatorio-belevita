#!/usr/bin/env python3
"""
Supabase Direct Extractor for Belevita ROI Dashboard
Connects directly to Supabase using the Python client library.
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from supabase import create_client, Client

from config.settings import AGENT_ID, CLIENT_ID, BATCH_SIZE, CACHE_DIR, CACHE_ENABLED, SUPABASE_PROJECT_REF

# Load environment variables
load_dotenv()


class SupabaseDirectExtractor:
    """
    Extracts data directly from Supabase using the official Python client.
    """

    def __init__(self):
        """
        Initialize Supabase client with credentials from .env
        """
        # Try different env var names
        self.supabase_key = (
            os.getenv("SUPABASE_SECRET_KEY") or 
            os.getenv("SUPABASE_KEY") or 
            os.getenv("SUPABASE_PUBLIC_KEY")
        )
        
        # Build URL from project ref or use env var
        self.supabase_url = os.getenv("SUPABASE_URL")
        if not self.supabase_url and SUPABASE_PROJECT_REF:
            self.supabase_url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Supabase credentials not found. Set in .env file:\n"
                "  SUPABASE_SECRET_KEY=your-service-role-key\n"
                "Or:\n"
                "  SUPABASE_URL=https://your-project.supabase.co\n"
                "  SUPABASE_KEY=your-anon-or-service-key"
            )
        
        print(f"Connecting to Supabase: {self.supabase_url[:50]}...")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        print("[OK] Connected to Supabase")

    def fetch_agent_sessions(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch agent sessions for Belevita.
        
        Args:
            limit: Maximum number of records to fetch
            
        Returns:
            List of session dictionaries
        """
        print(f"Fetching sessions for agent {AGENT_ID}, client {CLIENT_ID}...")
        
        query = self.client.table("agent_sessions").select(
            "id, lead_id, started_at, ended_at, agent_id, client_id, "
            "channel, cost, status, etapa, last_interaction, score, "
            "reason_interaction, analyse_sentimental, feedback"
        ).eq("agent_id", AGENT_ID).eq("client_id", CLIENT_ID).order("started_at", desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        sessions = response.data
        
        print(f"[OK] Fetched {len(sessions)} sessions")
        return sessions

    def fetch_chat_histories_by_phones(self, phones: List[str]) -> Dict[str, List[Dict]]:
        """
        Fetch chat histories for specific phone numbers (session_ids).
        
        Args:
            phones: List of phone numbers to fetch conversations for
            
        Returns:
            Dictionary mapping session_id to list of messages
        """
        if not phones:
            return {}
        
        print(f"Fetching chat histories for {len(phones)} phone numbers...")
        
        conversations = {}
        
        # Create phone variations for each phone
        all_phone_variations = set()
        for phone in phones:
            if phone:
                all_phone_variations.add(phone)
                all_phone_variations.add(phone.lstrip('+'))
                all_phone_variations.add('+' + phone.lstrip('+'))
        
        # Fetch in batches of 50 phones at a time (to avoid query limits)
        phone_list = list(all_phone_variations)
        
        for i in tqdm(range(0, len(phone_list), 50), desc="Fetching conversations"):
            batch_phones = phone_list[i:i+50]
            
            try:
                response = self.client.table("n8n_chat_histories").select(
                    "id, session_id, message"
                ).in_("session_id", batch_phones).order("id").execute()
                
                for chat in response.data:
                    session_id = chat.get('session_id')
                    if session_id:
                        if session_id not in conversations:
                            conversations[session_id] = []
                        conversations[session_id].append(chat)
                        
            except Exception as e:
                print(f"  Warning: Error fetching batch {i//50}: {e}")
                continue
        
        total_messages = sum(len(msgs) for msgs in conversations.values())
        print(f"[OK] Fetched {total_messages} messages from {len(conversations)} conversations")
        return conversations

    def fetch_leads(self, lead_ids: List[int]) -> Dict[int, Dict]:
        """
        Fetch lead information for given lead IDs.
        
        Args:
            lead_ids: List of lead IDs to fetch
            
        Returns:
            Dictionary mapping lead_id to lead data
        """
        if not lead_ids:
            return {}
        
        # Remove None values
        clean_ids = [lid for lid in lead_ids if lid is not None]
        
        if not clean_ids:
            return {}
        
        print(f"Fetching data for {len(clean_ids)} unique leads...")
        
        leads_dict = {}
        
        # Fetch in batches of 100 (Supabase limit)
        for i in tqdm(range(0, len(clean_ids), 100), desc="Fetching leads"):
            batch_ids = clean_ids[i:i+100]
            
            response = self.client.table("leads").select(
                "id, name, phone, email, created_at, client_id"
            ).in_("id", batch_ids).eq("client_id", CLIENT_ID).execute()
            
            for lead in response.data:
                leads_dict[lead['id']] = lead
        
        print(f"[OK] Fetched {len(leads_dict)} leads")
        return leads_dict

    def extract_all_data(self, session_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract all data needed for the dashboard.
        
        Args:
            session_limit: Limit number of sessions (for testing)
            
        Returns:
            Dictionary containing all extracted and correlated data
        """
        print("\n" + "=" * 60)
        print("EXTRACTING DATA FROM SUPABASE")
        print("=" * 60)
        
        # Step 1: Fetch agent sessions
        sessions = self.fetch_agent_sessions(limit=session_limit)
        
        # Step 2: Fetch leads
        lead_ids = list(set([s['lead_id'] for s in sessions if s.get('lead_id')]))
        leads_dict = self.fetch_leads(lead_ids)
        
        # Step 3: Extract phone numbers from leads
        phones = []
        for lead in leads_dict.values():
            if lead.get('phone'):
                phones.append(lead['phone'])
        
        print(f"Found {len(phones)} unique phone numbers from leads")
        
        # Step 4: Fetch chat histories only for those phones
        conversations_by_session = self.fetch_chat_histories_by_phones(phones)
        
        # Count total messages
        total_messages = sum(len(msgs) for msgs in conversations_by_session.values())
        
        # Step 5: Enrich sessions with messages
        # Match by phone number from leads
        enriched_sessions = []
        sessions_with_messages = 0
        
        for session in sessions:
            enriched = session.copy()
            
            # Add lead data
            lead_id = session.get('lead_id')
            if lead_id and lead_id in leads_dict:
                lead = leads_dict[lead_id]
                enriched['lead'] = lead
                
                # Try to find messages by phone
                phone = lead.get('phone', '')
                
                # Try different phone formats
                phone_variations = [
                    phone,
                    phone.lstrip('+'),
                    '+' + phone.lstrip('+'),
                    phone.replace('+', ''),
                ]
                
                messages = []
                for phone_var in phone_variations:
                    if phone_var and phone_var in conversations_by_session:
                        messages = conversations_by_session[phone_var]
                        break
                
                enriched['messages'] = messages
                enriched['message_count'] = len(messages)
                
                if messages:
                    sessions_with_messages += 1
            else:
                enriched['lead'] = None
                enriched['messages'] = []
                enriched['message_count'] = 0
            
            enriched_sessions.append(enriched)
        
        print(f"[OK] Correlated {sessions_with_messages} sessions with chat histories")
        
        result = {
            'sessions': enriched_sessions,
            'leads': list(leads_dict.values()),
            'chat_histories': [],  # Not storing full list anymore for memory efficiency
            'metadata': {
                'total_sessions': len(enriched_sessions),
                'total_leads': len(leads_dict),
                'total_messages': total_messages,
                'sessions_with_messages': sessions_with_messages,
                'agent_id': AGENT_ID,
                'client_id': CLIENT_ID,
                'extracted_at': datetime.now().isoformat(),
                'is_demo': False
            }
        }
        
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"  Sessions: {result['metadata']['total_sessions']}")
        print(f"  Leads: {result['metadata']['total_leads']}")
        print(f"  Messages: {result['metadata']['total_messages']}")
        print(f"  Sessions with messages: {result['metadata']['sessions_with_messages']}")
        
        return result


def save_extracted_data(data: Dict[str, Any], output_dir: str = CACHE_DIR):
    """
    Save extracted data to cache for faster subsequent processing.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    cache_file = os.path.join(output_dir, 'extracted_data.json')
    
    print(f"\nSaving extracted data to {cache_file}...")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print("[OK] Data saved successfully!")
    return cache_file


def load_cached_data(cache_dir: str = CACHE_DIR) -> Optional[Dict[str, Any]]:
    """
    Load previously extracted data from cache.
    """
    cache_file = os.path.join(cache_dir, 'extracted_data.json')
    
    if not os.path.exists(cache_file):
        return None
    
    print(f"Loading cached data from {cache_file}...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[OK] Loaded {data['metadata']['total_sessions']} sessions from cache")
    return data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract data from Supabase')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of sessions to extract (for testing)')
    parser.add_argument('--test', action='store_true',
                       help='Test connection with a small sample')
    
    args = parser.parse_args()
    
    try:
        extractor = SupabaseDirectExtractor()
        
        if args.test:
            print("\n--- TEST MODE: Extracting 10 sessions ---\n")
            data = extractor.extract_all_data(session_limit=10)
        else:
            data = extractor.extract_all_data(session_limit=args.limit)
        
        # Save to cache
        save_extracted_data(data)
        
        print("\nNext step: Run 'python scripts/generate_report.py --use-cache'")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nMake sure your .env file has:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_KEY=your-anon-or-service-key")
