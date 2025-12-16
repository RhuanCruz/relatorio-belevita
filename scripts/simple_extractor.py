#!/usr/bin/env python3
"""
Simplified Supabase Extractor for Belevita ROI Dashboard
Extracts data directly from n8n_chat_histories table.
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from supabase import create_client, Client

from config.settings import AGENT_ID, CLIENT_ID, CACHE_DIR, SUPABASE_PROJECT_REF

# Load environment variables
load_dotenv()


class SimplifiedExtractor:
    """
    Extracts data directly from n8n_chat_histories table.
    No correlation needed - just extract and analyze messages.
    """

    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_key = (
            os.getenv("SUPABASE_SECRET_KEY") or 
            os.getenv("SUPABASE_KEY") or 
            os.getenv("SUPABASE_PUBLIC_KEY")
        )
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        if not self.supabase_url and SUPABASE_PROJECT_REF:
            self.supabase_url = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in .env")
        
        print(f"Connecting to Supabase...")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        print("[OK] Connected")

    def fetch_chat_histories(self, limit: Optional[int] = None) -> Dict[str, List[Dict]]:
        """
        Fetch chat histories and group by session_id.
        
        Args:
            limit: Limit total messages to fetch
            
        Returns:
            Dictionary mapping session_id to list of messages
        """
        print(f"\nFetching chat histories from n8n_chat_histories...")
        
        conversations = defaultdict(list)
        offset = 0
        batch_size = 1000
        total_fetched = 0
        
        while True:
            try:
                response = self.client.table("n8n_chat_histories").select(
                    "id, session_id, message"
                ).order("id").range(offset, offset + batch_size - 1).execute()
                
                batch = response.data
                
                if not batch:
                    break
                
                for record in batch:
                    session_id = record.get('session_id')
                    if session_id:
                        conversations[session_id].append(record)
                
                total_fetched += len(batch)
                offset += batch_size
                
                print(f"  Fetched {total_fetched} messages, {len(conversations)} conversations...")
                
                if limit and total_fetched >= limit:
                    break
                    
            except Exception as e:
                print(f"  Warning: Error at offset {offset}: {e}")
                offset += batch_size
                continue
        
        print(f"[OK] Fetched {total_fetched} messages from {len(conversations)} conversations")
        return dict(conversations)

    def analyze_conversation(self, session_id: str, messages: List[Dict]) -> Dict[str, Any]:
        """
        Analyze a single conversation for errors and sentiment.
        
        Args:
            session_id: The conversation session ID
            messages: List of message records
            
        Returns:
            Analysis result for this conversation
        """
        # Extract message contents
        human_messages = []
        ai_messages = []
        all_content = []
        
        for msg_record in messages:
            msg_data = msg_record.get('message', {})
            if isinstance(msg_data, str):
                try:
                    msg_data = json.loads(msg_data)
                except:
                    msg_data = {'content': msg_data, 'type': 'unknown'}
            
            msg_type = msg_data.get('type', '')
            content = msg_data.get('content', '')
            
            if content:
                all_content.append(content.lower())
                
                if msg_type == 'human':
                    human_messages.append(content)
                elif msg_type == 'ai':
                    ai_messages.append(content)
        
        # Detect REAL errors - more specific phrases
        # Removed 'ajuda', 'suporte' as they are too common
        error_phrases = [
            'não entendi', 'nao entendi', 'não entendo', 'nao entendo',
            'erro', 'bug', 'travou', 'travado',
            'não funciona', 'nao funciona', 'não funcionou',
            'não consegui', 'nao consegui', 'não consigo',
            'errado', 'incorreto', 'falhou',
            'atendente humano', 'falar com humano', 'pessoa real', 'atendente real',
            'péssimo', 'horrível', 'ridículo', 'absurdo', 'lixo',
            'não respondeu', 'não resolve', 'não ajuda',
            'repetindo', 'já disse', 'não é isso'
        ]
        
        frustration_phrases = [
            'irritado', 'frustrado', 'cansado de', 'desisto', 
            'nunca mais', 'pior atendimento', 'demora demais',
            'inútil', 'incompetente', 'vergonha',
            'vou processar', 'procon', 'reclamação', 'reclame aqui'
        ]
        
        # Check for error indicators
        error_count = 0
        frustration_count = 0
        matched_phrases = []
        
        for content in all_content:
            for phrase in error_phrases:
                if phrase in content:
                    error_count += 1
                    matched_phrases.append(phrase)
            for phrase in frustration_phrases:
                if phrase in content:
                    frustration_count += 1
                    matched_phrases.append(phrase)
        
        # Calculate error score - adjusted weights
        # Single match = 15 points (was 20)
        # Multiple matches increase score
        error_score = min(100, error_count * 15 + frustration_count * 25)
        
        # Detect sentiment based on content
        positive_words = ['obrigado', 'obrigada', 'perfeito', 'ótimo', 'excelente', 'adorei', 'amei', 'top', 'maravilhoso']
        negative_words = ['ruim', 'péssimo', 'horrível', 'terrível', 'odiei', 'pior', 'lixo']
        
        positive_count = sum(1 for c in all_content for w in positive_words if w in c)
        negative_count = sum(1 for c in all_content for w in negative_words if w in c)
        
        if negative_count > positive_count:
            sentiment = 'Negativo'
        elif positive_count > negative_count:
            sentiment = 'Positivo'
        else:
            sentiment = 'Neutro'
        
        # Determine confidence level
        if error_score >= 70:
            confidence_level = 'high'
        elif error_score >= 40:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
        
        # Detect INTENT (Rastreio, Troca, Cancelamento, Dúvida)
        intent_keywords = {
            'Rastreio': [
                'rastrear', 'rastreio', 'rastreamento', 'onde está', 'onde esta',
                'cadê', 'cade', 'meu pedido', 'status do pedido', 'previsão',
                'entrega', 'chegou', 'quando chega', 'transportadora', 'correios'
            ],
            'Troca': [
                'trocar', 'troca', 'substituir', 'substituição', 'tamanho errado',
                'produto errado', 'defeito', 'defeituoso', 'veio errado',
                'diferente do pedido', 'não era isso', 'devolver'
            ],
            'Cancelamento': [
                'cancelar', 'cancelamento', 'cancela', 'desistir', 'desistência',
                'não quero mais', 'estornar', 'estorno', 'reembolso', 'dinheiro de volta'
            ],
            'Dúvida': [
                'dúvida', 'duvida', 'como funciona', 'como faço', 'como faz',
                'pode me explicar', 'informação', 'gostaria de saber', 'queria saber'
            ]
        }
        
        detected_intent = 'Outros'
        intent_score = 0
        
        for intent, keywords in intent_keywords.items():
            count = sum(1 for c in all_content for kw in keywords if kw in c)
            if count > intent_score:
                intent_score = count
                detected_intent = intent
        
        # Detect PRODUCT CATEGORIES mentioned
        product_categories = {
            'Calçados': ['sapato', 'tênis', 'tenis', 'sandália', 'sandalia', 'chinelo', 'bota', 'sapatilha', 'rasteira'],
            'Calças': ['calça', 'calca', 'jeans', 'legging', 'shorts', 'bermuda'],
            'Vestidos': ['vestido', 'dress'],
            'Blusas': ['blusa', 'camiseta', 'camisa', 'top', 'cropped', 'regata'],
            'Saias': ['saia'],
            'Conjuntos': ['conjunto', 'look'],
            'Acessórios': ['bolsa', 'cinto', 'colar', 'brinco', 'pulseira', 'óculos'],
            'Moda Íntima': ['sutiã', 'sutia', 'calcinha', 'lingerie', 'cueca'],
            'Moda Fitness': ['fitness', 'academia', 'yoga', 'esporte']
        }
        
        detected_products = []
        for category, keywords in product_categories.items():
            for c in all_content:
                for kw in keywords:
                    if kw in c:
                        detected_products.append(category)
                        break
        
        # Get unique products mentioned
        products_mentioned = list(set(detected_products))
        
        # Detect UNMET DEMANDS (what customers ask for that isn't available)
        unmet_demand_phrases = [
            'não tem', 'nao tem', 'não vende', 'nao vende', 
            'não encontrei', 'nao encontrei', 'acabou', 'esgotado',
            'não achei', 'nao achei', 'queria um', 'queria uma',
            'vocês vendem', 'voces vendem', 'tem disponível',
            'gostar de comprar', 'gostaria de encontrar',
            'não vi no site', 'nao vi no site'
        ]
        
        unmet_demands = []
        for c in all_content:
            for phrase in unmet_demand_phrases:
                if phrase in c:
                    # Extract context around the phrase
                    unmet_demands.append(c[:200])  # First 200 chars for context
                    break
        
        # If this is an error conversation, track which products are involved
        products_with_issues = []
        if error_score >= 40:  # Medium or high confidence error
            products_with_issues = products_mentioned.copy()
        
        return {
            'session_id': session_id,
            'message_count': len(messages),
            'human_messages': len(human_messages),
            'ai_messages': len(ai_messages),
            'error_score': error_score,
            'confidence_level': confidence_level,
            'sentiment': sentiment,
            'intent': detected_intent,
            'matched_phrases': list(set(matched_phrases)),
            'products_mentioned': products_mentioned,
            'products_with_issues': products_with_issues,
            'unmet_demands': unmet_demands[:3],  # Limit to 3 per conversation
            'messages': messages  # Keep raw messages for dashboard
        }

    def extract_and_analyze(self, message_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract all chat histories and analyze them.
        
        Args:
            message_limit: Limit total messages to fetch
            
        Returns:
            Complete analysis results
        """
        print("\n" + "=" * 60)
        print("EXTRACTING AND ANALYZING CHAT HISTORIES")
        print("=" * 60)
        
        # Fetch all conversations
        conversations = self.fetch_chat_histories(limit=message_limit)
        
        # Analyze each conversation
        print(f"\nAnalyzing {len(conversations)} conversations...")
        
        results = []
        high_confidence = 0
        medium_confidence = 0
        low_confidence = 0
        
        sentiment_counts = {'Positivo': 0, 'Neutro': 0, 'Negativo': 0}
        intent_counts = {'Rastreio': 0, 'Troca': 0, 'Cancelamento': 0, 'Dúvida': 0, 'Outros': 0}
        product_counts = {}  # Products mentioned overall
        products_with_issues_counts = {}  # Products in error conversations
        all_unmet_demands = []  # All unmet demands
        
        for session_id, messages in tqdm(conversations.items(), desc="Analyzing"):
            result = self.analyze_conversation(session_id, messages)
            results.append(result)
            
            # Count by confidence
            if result['confidence_level'] == 'high':
                high_confidence += 1
            elif result['confidence_level'] == 'medium':
                medium_confidence += 1
            else:
                low_confidence += 1
            
            # Count sentiment
            sentiment_counts[result['sentiment']] += 1
            
            # Count intent
            intent = result.get('intent', 'Outros')
            if intent in intent_counts:
                intent_counts[intent] += 1
            else:
                intent_counts['Outros'] += 1
            
            # Count products mentioned
            for product in result.get('products_mentioned', []):
                product_counts[product] = product_counts.get(product, 0) + 1
            
            # Count products with issues
            for product in result.get('products_with_issues', []):
                products_with_issues_counts[product] = products_with_issues_counts.get(product, 0) + 1
            
            # Collect unmet demands
            for demand in result.get('unmet_demands', []):
                all_unmet_demands.append({
                    'session_id': session_id,
                    'context': demand,
                    'error_score': result['error_score']
                })
        
        # Sort by error score
        results.sort(key=lambda x: x['error_score'], reverse=True)
        
        # Calculate metrics
        total_messages = sum(len(c) for c in conversations.values())
        total_conversations = len(conversations)
        
        # Create sessions format for compatibility with existing dashboard
        sessions = []
        for result in results:
            sessions.append({
                'id': result['session_id'],
                'started_at': datetime.now().isoformat(),  # Placeholder
                'ended_at': None,
                'status': 'completed' if result['error_score'] < 40 else 'active',
                'analyse_sentimental': result['sentiment'],
                'intent': result.get('intent', 'Outros'),
                'reason_interaction': result.get('intent', 'Outros'),
                'message_count': result['message_count'],
                'messages': result['messages'],
                'lead': {'name': result['session_id'][:20], 'phone': result['session_id']}
            })
        
        output = {
            'sessions': sessions,
            'leads': [],
            'chat_histories': [],
            'analysis_results': results,
            'metadata': {
                'total_sessions': total_conversations,
                'total_leads': 0,
                'total_messages': total_messages,
                'sessions_with_messages': total_conversations,
                'high_confidence_errors': high_confidence,
                'medium_confidence_errors': medium_confidence,
                'low_confidence_errors': low_confidence,
                'sentiment_distribution': sentiment_counts,
                'intent_distribution': intent_counts,
                'product_distribution': dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True)),
                'products_with_issues': dict(sorted(products_with_issues_counts.items(), key=lambda x: x[1], reverse=True)),
                'unmet_demands': all_unmet_demands[:100],  # Top 100 unmet demands
                'agent_id': AGENT_ID,
                'client_id': CLIENT_ID,
                'extracted_at': datetime.now().isoformat(),
                'is_demo': False
            }
        }
        
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"  Conversations: {total_conversations}")
        print(f"  Total messages: {total_messages}")
        print(f"  High confidence errors: {high_confidence}")
        print(f"  Medium confidence errors: {medium_confidence}")
        print(f"  Low confidence errors: {low_confidence}")
        print(f"  Sentiment: {sentiment_counts}")
        print(f"  Products mentioned: {product_counts}")
        print(f"  Products with issues: {products_with_issues_counts}")
        print(f"  Unmet demands found: {len(all_unmet_demands)}")
        
        return output


def save_extracted_data(data: Dict[str, Any], output_dir: str = CACHE_DIR):
    """Save extracted data to cache."""
    os.makedirs(output_dir, exist_ok=True)
    cache_file = os.path.join(output_dir, 'extracted_data.json')
    
    print(f"\nSaving to {cache_file}...")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print("[OK] Data saved!")
    return cache_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract and analyze chat histories')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit total messages to extract')
    parser.add_argument('--test', action='store_true',
                       help='Test with small sample (5000 messages)')
    
    args = parser.parse_args()
    
    try:
        extractor = SimplifiedExtractor()
        
        limit = args.limit
        if args.test:
            limit = 5000
            print("\n--- TEST MODE: 5000 messages ---\n")
        
        data = extractor.extract_and_analyze(message_limit=limit)
        save_extracted_data(data)
        
        print("\nNext step: Run 'python scripts/generate_report.py --use-cache --skip-ai-analysis'")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
