"""
Data Extractor for Belevita ROI Dashboard
Extracts and correlates data from Supabase tables using MCP tools.
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import pandas as pd

# Import settings
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import AGENT_ID, CLIENT_ID, BATCH_SIZE, CACHE_DIR, CACHE_ENABLED


class SupabaseMCPExtractor:
    """
    Extracts data from Supabase using MCP execute_sql function.
    This class assumes it's being run in an environment with MCP access.
    """

    def __init__(self, mcp_execute_sql_func):
        """
        Initialize with MCP execute_sql function.

        Args:
            mcp_execute_sql_func: Function that executes SQL via MCP
        """
        self.execute_sql = mcp_execute_sql_func

    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone numbers for correlation.
        Removes + prefix and non-digit characters.

        Args:
            phone: Phone number string

        Returns:
            Normalized phone number
        """
        if not phone:
            return ""

        # Remove all non-digit characters
        normalized = re.sub(r'\D', '', str(phone))
        return normalized

    def fetch_agent_sessions(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """
        Fetch agent sessions for Belevita.

        Args:
            limit: Maximum number of records to fetch
            offset: Number of records to skip

        Returns:
            List of session dictionaries
        """
        limit_clause = f"LIMIT {limit}" if limit else ""
        offset_clause = f"OFFSET {offset}" if offset > 0 else ""

        query = f"""
        SELECT
            id,
            lead_id,
            started_at,
            ended_at,
            agent_id,
            client_id,
            channel,
            cost,
            status,
            etapa,
            last_interaction,
            score,
            reason_interaction,
            analyse_sentimental,
            feedback
        FROM agent_sessions
        WHERE agent_id = {AGENT_ID} AND client_id = {CLIENT_ID}
        ORDER BY started_at DESC
        {limit_clause} {offset_clause};
        """

        result = self.execute_sql(query)
        return json.loads(result) if isinstance(result, str) else result

    def fetch_leads(self, lead_ids: List[int]) -> List[Dict]:
        """
        Fetch lead information for given lead IDs.

        Args:
            lead_ids: List of lead IDs to fetch

        Returns:
            List of lead dictionaries
        """
        if not lead_ids:
            return []

        # Remove None values and convert to string
        clean_ids = [str(lid) for lid in lead_ids if lid is not None]

        if not clean_ids:
            return []

        ids_str = ",".join(clean_ids)

        query = f"""
        SELECT
            id,
            name,
            phone,
            email,
            created_at,
            client_id
        FROM leads
        WHERE id IN ({ids_str}) AND client_id = {CLIENT_ID};
        """

        result = self.execute_sql(query)
        return json.loads(result) if isinstance(result, str) else result

    def fetch_chat_histories_by_phones(self, phones: List[str]) -> List[Dict]:
        """
        Fetch chat histories for given phone numbers.

        Args:
            phones: List of normalized phone numbers

        Returns:
            List of chat history dictionaries
        """
        if not phones:
            return []

        # Create list of phone variations (with and without + prefix)
        phone_variations = []
        for phone in phones:
            phone_variations.append(f"'{phone}'")
            phone_variations.append(f"'+{phone}'")

        phones_str = ",".join(phone_variations)

        query = f"""
        SELECT
            id,
            session_id,
            message
        FROM n8n_chat_histories
        WHERE session_id IN ({phones_str})
        ORDER BY id;
        """

        result = self.execute_sql(query)
        return json.loads(result) if isinstance(result, str) else result

    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extract all data needed for the dashboard.
        Performs correlation between sessions, leads, and chat histories.

        Returns:
            Dictionary containing all extracted and correlated data
        """
        print("Extracting data from Supabase...")

        # Step 1: Fetch all agent sessions
        print(f"Fetching sessions for agent {AGENT_ID}...")
        sessions = []
        offset = 0

        while True:
            batch = self.fetch_agent_sessions(limit=BATCH_SIZE, offset=offset)
            if not batch:
                break

            sessions.extend(batch)
            offset += BATCH_SIZE
            print(f"  Fetched {len(sessions)} sessions so far...")

            # Safety limit for development
            if len(sessions) >= 100000:
                print("  Reached safety limit of 100K sessions")
                break

        print(f"Total sessions fetched: {len(sessions)}")

        # Step 2: Extract unique lead IDs
        lead_ids = list(set([s['lead_id'] for s in sessions if s.get('lead_id')]))
        print(f"Fetching data for {len(lead_ids)} unique leads...")

        # Fetch leads in batches
        leads_dict = {}
        for i in tqdm(range(0, len(lead_ids), 1000), desc="Fetching leads"):
            batch_ids = lead_ids[i:i+1000]
            leads_batch = self.fetch_leads(batch_ids)
            for lead in leads_batch:
                leads_dict[lead['id']] = lead

        print(f"Fetched {len(leads_dict)} leads")

        # Step 3: Normalize phones and fetch chat histories
        phones = []
        for lead in leads_dict.values():
            if lead.get('phone'):
                normalized = self.normalize_phone(lead['phone'])
                if normalized:
                    phones.append(normalized)

        unique_phones = list(set(phones))
        print(f"Fetching chat histories for {len(unique_phones)} unique phones...")

        # Fetch chat histories in batches
        chat_histories = []
        for i in tqdm(range(0, len(unique_phones), 500), desc="Fetching conversations"):
            batch_phones = unique_phones[i:i+500]
            histories_batch = self.fetch_chat_histories_by_phones(batch_phones)
            chat_histories.extend(histories_batch)

        print(f"Fetched {len(chat_histories)} chat messages")

        # Step 4: Correlate data
        print("Correlating data...")

        # Create phone -> lead mapping
        phone_to_lead = {}
        for lead in leads_dict.values():
            if lead.get('phone'):
                normalized = self.normalize_phone(lead['phone'])
                phone_to_lead[normalized] = lead

        # Create session_id -> conversations mapping
        conversations = {}
        for chat in chat_histories:
            session_id = chat.get('session_id')
            if session_id:
                # Normalize session_id (phone number)
                normalized_session = self.normalize_phone(session_id)

                if normalized_session not in conversations:
                    conversations[normalized_session] = []

                conversations[normalized_session].append(chat)

        # Enrich sessions with lead and conversation data
        enriched_sessions = []
        for session in sessions:
            enriched = session.copy()

            # Add lead data
            lead_id = session.get('lead_id')
            if lead_id and lead_id in leads_dict:
                enriched['lead'] = leads_dict[lead_id]

                # Add conversation data
                lead_phone = leads_dict[lead_id].get('phone')
                if lead_phone:
                    normalized_phone = self.normalize_phone(lead_phone)
                    if normalized_phone in conversations:
                        enriched['messages'] = conversations[normalized_phone]
                        enriched['message_count'] = len(conversations[normalized_phone])
                    else:
                        enriched['messages'] = []
                        enriched['message_count'] = 0
                else:
                    enriched['messages'] = []
                    enriched['message_count'] = 0
            else:
                enriched['lead'] = None
                enriched['messages'] = []
                enriched['message_count'] = 0

            enriched_sessions.append(enriched)

        print(f"Correlated {len(enriched_sessions)} sessions with conversations")

        return {
            'sessions': enriched_sessions,
            'leads': list(leads_dict.values()),
            'chat_histories': chat_histories,
            'metadata': {
                'total_sessions': len(enriched_sessions),
                'total_leads': len(leads_dict),
                'total_messages': len(chat_histories),
                'agent_id': AGENT_ID,
                'client_id': CLIENT_ID,
                'extracted_at': datetime.now().isoformat()
            }
        }


def save_extracted_data(data: Dict[str, Any], output_dir: str = CACHE_DIR):
    """
    Save extracted data to cache for faster subsequent processing.

    Args:
        data: Extracted data dictionary
        output_dir: Directory to save cache files
    """
    os.makedirs(output_dir, exist_ok=True)

    cache_file = os.path.join(output_dir, 'extracted_data.json')

    print(f"Saving extracted data to {cache_file}...")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Data saved successfully!")


def load_cached_data(cache_dir: str = CACHE_DIR) -> Optional[Dict[str, Any]]:
    """
    Load previously extracted data from cache.

    Args:
        cache_dir: Directory containing cache files

    Returns:
        Cached data dictionary or None if cache doesn't exist
    """
    cache_file = os.path.join(cache_dir, 'extracted_data.json')

    if not os.path.exists(cache_file):
        return None

    print(f"Loading cached data from {cache_file}...")
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {data['metadata']['total_sessions']} sessions from cache")
    return data


if __name__ == "__main__":
    print("Data Extractor for Belevita ROI Dashboard")
    print("=" * 50)
    print("This module is meant to be imported and used with MCP access.")
    print("Run generate_report.py to extract data and generate the dashboard.")
