#!/usr/bin/env python3
"""
Create Demo Data for Belevita Dashboard
Generates sample data with ~1000 sessions for demonstration purposes
"""

import json
import os
import sys
from datetime import datetime
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.settings import OUTPUT_DIR, CACHE_DIR

# Sample sessions data (1000 sessions from most recent)
# This will be populated by Claude via MCP queries

def create_demo_data():
    """
    Create demo dataset with realistic distributions
    """

    print("Creating demo data for Belevita Dashboard...")
    print("=" * 60)

    # For demo purposes, we'll create a simplified dataset
    # In production, this would come from the actual extraction

    demo_sessions = []

    # Generate 100 sample sessions with varied attributes
    statuses = ['completed', 'active']
    sentiments = ['Positivo', 'Neutro', 'Negativo']
    reasons = ['Rastreio', 'Cancelamento', 'Troca', 'Informação geral', 'Suporte']

    for i in range(100):
        session = {
            'id': 39500 + i,
            'lead_id': 122500 + i if random.random() > 0.3 else None,
            'started_at': f"2025-12-{15 - i//10:02d} {10 + i%12:02d}:30:00",
            'ended_at': f"2025-12-{15 - i//10:02d} {11 + i%12:02d}:00:00" if random.random() > 0.3 else None,
            'agent_id': 19,
            'client_id': 6,
            'channel': 'whatsapp',
            'status': random.choice(statuses),
            'score': str(random.randint(7, 10)) if random.random() > 0.3 else None,
            'reason_interaction': random.choice(reasons),
            'analyse_sentimental': random.choice(sentiments),
            'feedback': None,
            'message_count': random.randint(3, 15),
            'lead': {
                'name': f'Cliente Demo {i}',
                'phone': f'5511999{i:06d}',
                'email': f'cliente{i}@example.com'
            } if random.random() > 0.3 else None,
            'messages': [
                {
                    'id': f'msg_{i}_1',
                    'message': {
                        'type': 'human',
                        'content': 'Olá, gostaria de saber sobre meu pedido'
                    }
                },
                {
                    'id': f'msg_{i}_2',
                    'message': {
                        'type': 'ai',
                        'content': 'Olá! Posso ajudar com informações sobre seu pedido. Por favor, me informe o número do pedido.'
                    }
                }
            ]
        }
        demo_sessions.append(session)

    # Create extracted_data structure
    extracted_data = {
        'sessions': demo_sessions,
        'leads': [s['lead'] for s in demo_sessions if s.get('lead')],
        'chat_histories': [],
        'metadata': {
            'total_sessions': len(demo_sessions),
            'total_leads': len([s for s in demo_sessions if s.get('lead')]),
            'total_messages': sum(s['message_count'] for s in demo_sessions),
            'agent_id': 19,
            'client_id': 6,
            'extracted_at': datetime.now().isoformat(),
            'is_demo': True
        }
    }

    # Save to cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, 'extracted_data.json')

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Demo data created successfully!")
    print(f"  Sessions: {extracted_data['metadata']['total_sessions']}")
    print(f"  Leads: {extracted_data['metadata']['total_leads']}")
    print(f"  Messages: {extracted_data['metadata']['total_messages']}")
    print(f"\nSaved to: {cache_file}")
    print("\nNext step: Run 'python scripts/generate_report.py --use-cache'")


if __name__ == "__main__":
    create_demo_data()
