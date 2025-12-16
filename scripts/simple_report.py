#!/usr/bin/env python3
"""
Simplified Report Generator for Belevita ROI Dashboard
Works with data from simple_extractor.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import OUTPUT_DIR, CACHE_DIR


def load_cached_data():
    """Load data from cache."""
    cache_file = os.path.join(CACHE_DIR, 'extracted_data.json')
    
    if not os.path.exists(cache_file):
        print(f"[ERROR] Cache file not found: {cache_file}")
        print("Run 'python scripts/simple_extractor.py' first")
        return None
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict, filename: str):
    """Save JSON to output directory."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[OK] Saved {filename}")


def generate_report():
    """Generate all dashboard JSON files."""
    print("=" * 60)
    print("SIMPLIFIED REPORT GENERATOR")
    print("=" * 60)
    
    # Load data
    data = load_cached_data()
    if not data:
        return
    
    sessions = data['sessions']
    metadata = data['metadata']
    analysis_results = data.get('analysis_results', [])
    
    print(f"Loaded {len(sessions)} sessions")
    
    # 1. Summary
    summary = {
        'overview': {
            'total_sessions': metadata['total_sessions'],
            'total_leads': metadata.get('total_leads', 0),
            'total_messages': metadata['total_messages'],
            'agent_id': metadata['agent_id'],
            'client_id': metadata['client_id'],
            'date_range': {
                'start': metadata['extracted_at'],
                'end': metadata['extracted_at']
            },
            'generated_at': datetime.now().isoformat()
        },
        'key_metrics': {
            'total_sessions': metadata['total_sessions'],
            'unique_leads': metadata.get('total_leads', 0),
            'resolution_rate': round(
                (metadata['low_confidence_errors'] / metadata['total_sessions'] * 100) 
                if metadata['total_sessions'] > 0 else 0, 2
            ),
            'positive_sentiment_rate': round(
                (metadata['sentiment_distribution']['Positivo'] / metadata['total_sessions'] * 100)
                if metadata['total_sessions'] > 0 else 0, 2
            ),
            'avg_sessions_per_day': metadata['total_sessions'],
            'median_response_time': 0
        },
        'error_summary': {
            'total_analyzed': metadata['total_sessions'],
            'high_confidence_errors': metadata['high_confidence_errors'],
            'medium_confidence_errors': metadata['medium_confidence_errors'],
            'error_rate': round(
                ((metadata['high_confidence_errors'] + metadata['medium_confidence_errors']) / 
                 metadata['total_sessions'] * 100) if metadata['total_sessions'] > 0 else 0, 2
            )
        }
    }
    save_json(summary, 'summary.json')
    
    # 2. Daily metrics (simplified)
    daily_metrics = {
        'volume': {
            'daily': [],
            'weekly': [],
            'monthly': [],
            'hourly_distribution': [{'hour': h, 'sessions_count': 0} for h in range(24)],
            'daily_unique_leads': [],
            'total_sessions': metadata['total_sessions'],
            'total_unique_leads': 0,
            'average_sessions_per_day': metadata['total_sessions'],
            'peak_hour': 10
        },
        'response_time': {
            'daily': [],
            'overall_median': 0,
            'overall_average': 0,
            'overall_p95': 0,
            'outliers_count': 0
        },
        'resolution_rate': {
            'overall_rate': round(
                (metadata['low_confidence_errors'] / metadata['total_sessions'] * 100) 
                if metadata['total_sessions'] > 0 else 0, 2
            ),
            'total_sessions': metadata['total_sessions'],
            'completed_sessions': metadata['low_confidence_errors'],
            'active_sessions': metadata['high_confidence_errors'] + metadata['medium_confidence_errors'],
            'failed_sessions': 0,
            'breakdown_by_reason': [],
            'weekly_trend': []
        },
        'sentiment': metadata['sentiment_distribution'],
        'metadata': {
            'calculated_at': datetime.now().isoformat(),
            'total_sessions_analyzed': metadata['total_sessions'],
            'date_range': {
                'start': metadata['extracted_at'],
                'end': metadata['extracted_at']
            }
        }
    }
    save_json(daily_metrics, 'daily_metrics.json')
    
    # 3. Sentiment analysis
    total = metadata['total_sessions']
    sentiment_data = {
        'distribution': metadata['sentiment_distribution'],
        'percentages': {
            'Positivo': round(metadata['sentiment_distribution']['Positivo'] / total * 100, 2) if total > 0 else 0,
            'Neutro': round(metadata['sentiment_distribution']['Neutro'] / total * 100, 2) if total > 0 else 0,
            'Negativo': round(metadata['sentiment_distribution']['Negativo'] / total * 100, 2) if total > 0 else 0,
        },
        'weekly_trend': [],
        'correlation_with_resolution': {},
        'positive_rate': round(metadata['sentiment_distribution']['Positivo'] / total * 100, 2) if total > 0 else 0,
        'negative_rate': round(metadata['sentiment_distribution']['Negativo'] / total * 100, 2) if total > 0 else 0
    }
    save_json(sentiment_data, 'sentiment_analysis.json')
    
    # 4. Error analysis
    error_results = []
    error_categories = {}
    
    for result in analysis_results:
        error_results.append({
            'session_id': result['session_id'],
            'confidence_score': result['error_score'],
            'confidence_level': result['confidence_level'],
            'phrase_detection': {
                'score': result['error_score'],
                'matched_phrases': result['matched_phrases'],
                'categories': {},
                'total_matches': len(result['matched_phrases'])
            },
            'behavioral_patterns': {
                'score': 0,
                'patterns': [],
                'pattern_count': 0
            },
            'sentiment_correlation': {
                'score': 50 if result['sentiment'] == 'Negativo' else 10,
                'sentiment': result['sentiment'],
                'reasoning': f"Sentiment: {result['sentiment']}"
            },
            'has_error': result['confidence_level'] in ['high', 'medium']
        })
        
        # Count error categories
        for phrase in result['matched_phrases']:
            error_categories[phrase] = error_categories.get(phrase, 0) + 1
    
    error_analysis = {
        'total_sessions': metadata['total_sessions'],
        'analyzed_sessions': len(error_results),
        'high_confidence_errors': metadata['high_confidence_errors'],
        'medium_confidence_errors': metadata['medium_confidence_errors'],
        'low_confidence_errors': metadata['low_confidence_errors'],
        'error_categories': error_categories,
        'intent_distribution': metadata.get('intent_distribution', {}),
        'results': error_results,
        'metadata': {
            'analyzed_at': datetime.now().isoformat(),
            'methods_used': ['phrase_matching', 'sentiment_correlation']
        }
    }
    save_json(error_analysis, 'error_analysis.json')
    
    # 5. Conversation samples (top 500 by error score)
    samples = []
    for result in analysis_results[:500]:
        session = next((s for s in sessions if s['id'] == result['session_id']), None)
        if session:
            samples.append({
                'session_id': result['session_id'],
                'started_at': session.get('started_at'),
                'ended_at': session.get('ended_at'),
                'status': session.get('status', 'unknown'),
                'sentiment': result['sentiment'],
                'intent': result.get('intent', 'Outros'),
                'error_confidence': result['error_score'],
                'error_level': result['confidence_level'],
                'matched_phrases': result.get('matched_phrases', []),
                'messages': session.get('messages', []),
                'lead': session.get('lead', {'name': 'Unknown', 'phone': ''})
            })
    
    save_json(samples, 'conversation_samples.json')
    
    # 6. Sessions summary
    sessions_summary = []
    for session in sessions:
        result = next((r for r in analysis_results if r['session_id'] == session['id']), None)
        sessions_summary.append({
            'id': session['id'],
            'started_at': session.get('started_at'),
            'ended_at': session.get('ended_at'),
            'status': session.get('status', 'unknown'),
            'sentiment': result['sentiment'] if result else None,
            'intent': result.get('intent', 'Outros') if result else None,
            'reason': session.get('intent', 'Outros'),
            'message_count': session.get('message_count', 0)
        })
    
    save_json({'sessions': sessions_summary}, 'sessions_summary.json')
    
    # 7. Relatório em texto para cliente (Markdown-like)
    intent_dist = metadata.get('intent_distribution', {})
    report_text = {
        'titulo': 'Relatório de Análise de Atendimentos - Belevita',
        'resumo_executivo': f"""
Foram analisadas {metadata['total_sessions']:,} conversas com um total de {metadata['total_messages']:,} mensagens.

### Principais Descobertas:

**Qualidade do Atendimento:**
- {metadata['low_confidence_errors']:,} conversas ({round(metadata['low_confidence_errors']/metadata['total_sessions']*100, 1)}%) foram concluídas sem problemas identificados
- {metadata['high_confidence_errors'] + metadata['medium_confidence_errors']:,} conversas ({round((metadata['high_confidence_errors'] + metadata['medium_confidence_errors'])/metadata['total_sessions']*100, 1)}%) apresentaram possíveis problemas

**Satisfação do Cliente:**
- {metadata['sentiment_distribution']['Positivo']:,} conversas com sentimento positivo ({round(metadata['sentiment_distribution']['Positivo']/metadata['total_sessions']*100, 1)}%)
- {metadata['sentiment_distribution']['Neutro']:,} conversas com sentimento neutro ({round(metadata['sentiment_distribution']['Neutro']/metadata['total_sessions']*100, 1)}%)
- {metadata['sentiment_distribution']['Negativo']:,} conversas com sentimento negativo ({round(metadata['sentiment_distribution']['Negativo']/metadata['total_sessions']*100, 1)}%)

**Principais Motivos de Contato:**
- Rastreio de Pedidos: {intent_dist.get('Rastreio', 0):,} conversas
- Trocas e Devoluções: {intent_dist.get('Troca', 0):,} conversas
- Cancelamentos: {intent_dist.get('Cancelamento', 0):,} conversas
- Dúvidas Gerais: {intent_dist.get('Dúvida', 0):,} conversas
- Outros Assuntos: {intent_dist.get('Outros', 0):,} conversas
""",
        'problemas_identificados': {
            'conversas_com_erros_graves': metadata['high_confidence_errors'],
            'descricao_erros_graves': 'Conversas onde o cliente expressou frustração clara, mencionou PROCON, ou pediu atendente humano múltiplas vezes.',
            'conversas_com_possiveis_problemas': metadata['medium_confidence_errors'],
            'descricao_possiveis_problemas': 'Conversas onde o cliente disse "não entendi" ou demonstrou alguma dificuldade.',
            'top_frases_erro': dict(sorted(error_categories.items(), key=lambda x: x[1], reverse=True)[:10])
        },
        'intencoes': intent_dist,
        'sentimento': metadata['sentiment_distribution'],
        'produtos': {
            'mais_mencionados': metadata.get('product_distribution', {}),
            'com_problemas': metadata.get('products_with_issues', {}),
            'analise': 'Produtos que aparecem em conversas com erros identificados. Indica possíveis problemas de qualidade, tamanho ou entrega.'
        },
        'demandas_nao_atendidas': {
            'total': len(metadata.get('unmet_demands', [])),
            'exemplos': metadata.get('unmet_demands', [])[:20],
            'analise': 'Frases onde clientes perguntaram sobre produtos ou serviços que a Belevita não oferece atualmente.'
        }
    }
    save_json(report_text, 'report_text.json')
    
    # 8. Separate products analysis file
    products_analysis = {
        'produtos_mais_mencionados': metadata.get('product_distribution', {}),
        'produtos_com_problemas': metadata.get('products_with_issues', {}),
        'demandas_nao_atendidas': metadata.get('unmet_demands', [])[:50],
        'analise_resumo': f"""
## Análise de Produtos

### Categorias Mais Mencionadas:
{chr(10).join([f"- **{k}**: {v} menções" for k, v in list(metadata.get('product_distribution', {}).items())[:5]])}

### Categorias com Mais Problemas:
{chr(10).join([f"- **{k}**: {v} conversas com problemas" for k, v in list(metadata.get('products_with_issues', {}).items())[:5]])}

### Oportunidades de Melhoria:
Foram identificadas {len(metadata.get('unmet_demands', []))} situações onde clientes perguntaram sobre produtos ou serviços não disponíveis.
"""
    }
    save_json(products_analysis, 'products_analysis.json')
    
    print("\n" + "=" * 60)
    print("REPORT GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nTotal conversations: {metadata['total_sessions']}")
    print(f"High confidence errors: {metadata['high_confidence_errors']}")
    print(f"Medium confidence errors: {metadata['medium_confidence_errors']}")
    print(f"Error rate: {summary['error_summary']['error_rate']}%")
    print(f"\nNext step: Open http://localhost:8080/dashboard/")


if __name__ == "__main__":
    generate_report()
