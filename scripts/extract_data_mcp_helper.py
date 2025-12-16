#!/usr/bin/env python3
"""
MCP Data Extraction Helper
This script provides SQL queries that Claude can execute via MCP tools.
Results are saved progressively to cache.
"""

import json
import os
import re
from datetime import datetime

# Import settings
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import AGENT_ID, CLIENT_ID, BATCH_SIZE, CACHE_DIR

# This will store extracted data as we go
extracted_data = {
    'sessions': [],
    'leads_dict': {},
    'chat_histories': [],
    'metadata': {
        'agent_id': AGENT_ID,
        'client_id': CLIENT_ID,
        'extracted_at': datetime.now().isoformat()
    }
}


def normalize_phone(phone: str) -> str:
    """Normalize phone numbers for correlation."""
    if not phone:
        return ""
    normalized = re.sub(r'\D', '', str(phone))
    return normalized


def load_progress():
    """Load extraction progress if it exists."""
    global extracted_data
    progress_file = os.path.join(CACHE_DIR, 'extraction_progress.json')
    if os.path.exists(progress_file):
        print(f"Loading progress from {progress_file}...")
        with open(progress_file, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
        print(f"Loaded {len(extracted_data['sessions'])} sessions from progress file")
    return extracted_data


def save_progress():
    """Save current extraction progress."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    progress_file = os.path.join(CACHE_DIR, 'extraction_progress.json')
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    print(f"Progress saved: {len(extracted_data['sessions'])} sessions")


def add_sessions_batch(sessions_json: str):
    """Add a batch of sessions to extracted data."""
    sessions = json.loads(sessions_json)
    extracted_data['sessions'].extend(sessions)
    print(f"Added {len(sessions)} sessions. Total: {len(extracted_data['sessions'])}")
    save_progress()


def add_leads_batch(leads_json: str):
    """Add a batch of leads to extracted data."""
    leads = json.loads(leads_json)
    for lead in leads:
        extracted_data['leads_dict'][lead['id']] = lead
    print(f"Added {len(leads)} leads. Total: {len(extracted_data['leads_dict'])}")
    save_progress()


def add_chat_histories_batch(chats_json: str):
    """Add a batch of chat histories to extracted data."""
    chats = json.loads(chats_json)
    extracted_data['chat_histories'].extend(chats)
    print(f"Added {len(chats)} messages. Total: {len(extracted_data['chat_histories'])}")
    save_progress()


def correlate_data():
    """Correlate sessions with leads and chat histories."""
    print("\nCorrelating data...")

    # Create phone -> lead mapping
    phone_to_lead = {}
    for lead in extracted_data['leads_dict'].values():
        if lead.get('phone'):
            normalized = normalize_phone(lead['phone'])
            phone_to_lead[normalized] = lead

    # Create session_id -> conversations mapping
    conversations = {}
    for chat in extracted_data['chat_histories']:
        session_id = chat.get('session_id')
        if session_id:
            normalized_session = normalize_phone(session_id)
            if normalized_session not in conversations:
                conversations[normalized_session] = []
            conversations[normalized_session].append(chat)

    # Enrich sessions
    enriched_sessions = []
    for session in extracted_data['sessions']:
        enriched = session.copy()

        # Add lead data
        lead_id = session.get('lead_id')
        if lead_id and lead_id in extracted_data['leads_dict']:
            enriched['lead'] = extracted_data['leads_dict'][lead_id]

            # Add conversation data
            lead_phone = extracted_data['leads_dict'][lead_id].get('phone')
            if lead_phone:
                normalized_phone = normalize_phone(lead_phone)
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

    # Update metadata
    extracted_data['sessions'] = enriched_sessions
    extracted_data['metadata']['total_sessions'] = len(enriched_sessions)
    extracted_data['metadata']['total_leads'] = len(extracted_data['leads_dict'])
    extracted_data['metadata']['total_messages'] = len(extracted_data['chat_histories'])

    print(f"Correlated {len(enriched_sessions)} sessions")
    print(f"  - With lead data: {sum(1 for s in enriched_sessions if s.get('lead'))}")
    print(f"  - With messages: {sum(1 for s in enriched_sessions if s.get('message_count', 0) > 0)}")

    # Save final result
    cache_file = os.path.join(CACHE_DIR, 'extracted_data.json')
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Final data saved to {cache_file}")


if __name__ == "__main__":
    print("MCP Data Extraction Helper")
    print("=" * 50)
    print("This module provides functions for Claude to extract data via MCP.")
    print("\nUsage:")
    print("  1. Claude executes SQL queries via MCP")
    print("  2. Results are passed to add_*_batch() functions")
    print("  3. Progress is saved incrementally")
    print("  4. Finally, correlate_data() combines everything")
