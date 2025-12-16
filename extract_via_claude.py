#!/usr/bin/env python3
"""
Claude-Assisted Data Extraction Script
This script will be run manually by the user while Claude executes MCP queries.
Saves results incrementally to avoid data loss.
"""

import json
import os
import re
from datetime import datetime

# Configuration
CACHE_DIR = "output/cache"
OUTPUT_FILE = os.path.join(CACHE_DIR, "extracted_data.json")
BATCH_DIR = os.path.join(CACHE_DIR, "batches")

# Ensure directories exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(BATCH_DIR, exist_ok=True)

def normalize_phone(phone: str) -> str:
    """Normalize phone numbers for correlation."""
    if not phone:
        return ""
    normalized = re.sub(r'\D', '', str(phone))
    return normalized


def save_sessions_batch(batch_data: list, batch_num: int):
    """Save a batch of sessions."""
    filename = os.path.join(BATCH_DIR, f"sessions_batch_{batch_num}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved batch {batch_num}: {len(batch_data)} sessions")


def save_leads_batch(batch_data: list, batch_num: int):
    """Save a batch of leads."""
    filename = os.path.join(BATCH_DIR, f"leads_batch_{batch_num}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved batch {batch_num}: {len(batch_data)} leads")


def save_chats_batch(batch_data: list, batch_num: int):
    """Save a batch of chat histories."""
    filename = os.path.join(BATCH_DIR, f"chats_batch_{batch_num}.json")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved batch {batch_num}: {len(batch_data)} chats")


def load_all_batches():
    """Load and combine all batches."""
    print("\nLoading all batches...")

    sessions = []
    leads_dict = {}
    chat_histories = []

    # Load session batches
    session_files = sorted([f for f in os.listdir(BATCH_DIR) if f.startswith('sessions_batch_')])
    for filename in session_files:
        filepath = os.path.join(BATCH_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            batch = json.load(f)
            sessions.extend(batch)
    print(f"  Loaded {len(sessions)} sessions from {len(session_files)} batches")

    # Load lead batches
    lead_files = sorted([f for f in os.listdir(BATCH_DIR) if f.startswith('leads_batch_')])
    for filename in lead_files:
        filepath = os.path.join(BATCH_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            batch = json.load(f)
            for lead in batch:
                leads_dict[lead['id']] = lead
    print(f"  Loaded {len(leads_dict)} leads from {len(lead_files)} batches")

    # Load chat batches
    chat_files = sorted([f for f in os.listdir(BATCH_DIR) if f.startswith('chats_batch_')])
    for filename in chat_files:
        filepath = os.path.join(BATCH_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            batch = json.load(f)
            chat_histories.extend(batch)
    print(f"  Loaded {len(chat_histories)} chat messages from {len(chat_files)} batches")

    return sessions, leads_dict, chat_histories


def correlate_and_save():
    """Correlate all data and save final output."""
    print("\n" + "=" * 60)
    print("CORRELATING DATA")
    print("=" * 60)

    sessions, leads_dict, chat_histories = load_all_batches()

    # Create phone -> lead mapping
    print("\nCreating phone-to-lead mapping...")
    phone_to_lead = {}
    for lead in leads_dict.values():
        if lead.get('phone'):
            normalized = normalize_phone(lead['phone'])
            phone_to_lead[normalized] = lead
    print(f"  {len(phone_to_lead)} unique phones mapped")

    # Create session_id -> conversations mapping
    print("\nCreating session-to-conversations mapping...")
    conversations = {}
    for chat in chat_histories:
        session_id = chat.get('session_id')
        if session_id:
            normalized_session = normalize_phone(session_id)
            if normalized_session not in conversations:
                conversations[normalized_session] = []
            conversations[normalized_session].append(chat)
    print(f"  {len(conversations)} unique conversation threads")

    # Enrich sessions
    print("\nEnriching sessions with lead and conversation data...")
    enriched_sessions = []
    sessions_with_lead = 0
    sessions_with_messages = 0

    for session in sessions:
        enriched = session.copy()

        # Add lead data
        lead_id = session.get('lead_id')
        if lead_id and lead_id in leads_dict:
            enriched['lead'] = leads_dict[lead_id]
            sessions_with_lead += 1

            # Add conversation data
            lead_phone = leads_dict[lead_id].get('phone')
            if lead_phone:
                normalized_phone = normalize_phone(lead_phone)
                if normalized_phone in conversations:
                    enriched['messages'] = conversations[normalized_phone]
                    enriched['message_count'] = len(conversations[normalized_phone])
                    sessions_with_messages += 1
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

    print(f"  Total sessions: {len(enriched_sessions)}")
    print(f"  Sessions with lead data: {sessions_with_lead}")
    print(f"  Sessions with messages: {sessions_with_messages}")

    # Create final output
    extracted_data = {
        'sessions': enriched_sessions,
        'leads': list(leads_dict.values()),
        'chat_histories': chat_histories,
        'metadata': {
            'total_sessions': len(enriched_sessions),
            'total_leads': len(leads_dict),
            'total_messages': len(chat_histories),
            'sessions_with_lead': sessions_with_lead,
            'sessions_with_messages': sessions_with_messages,
            'agent_id': 19,
            'client_id': 6,
            'extracted_at': datetime.now().isoformat()
        }
    }

    # Save final output
    print(f"\nSaving final output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("✓ DATA EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"\nFinal stats:")
    print(f"  Sessions: {extracted_data['metadata']['total_sessions']:,}")
    print(f"  Leads: {extracted_data['metadata']['total_leads']:,}")
    print(f"  Messages: {extracted_data['metadata']['total_messages']:,}")
    print(f"\nOutput file: {OUTPUT_FILE}")
    print("\nNext step: Run generate_report.py --use-cache")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "correlate":
        correlate_and_save()
    else:
        print("Claude-Assisted Data Extraction Helper")
        print("=" * 60)
        print("\nUsage:")
        print("  1. Claude will execute MCP queries and save batches")
        print("  2. Run: python extract_via_claude.py correlate")
        print("\nBatch saving functions available:")
        print("  - save_sessions_batch(data, batch_num)")
        print("  - save_leads_batch(data, batch_num)")
        print("  - save_chats_batch(data, batch_num)")
