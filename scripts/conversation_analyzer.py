"""
Conversation Analyzer for Belevita ROI Dashboard
Uses Google Gemini API to analyze conversations for errors and quality.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import google.generativeai as genai

# Import settings
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    GOOGLE_API_KEY,
    AI_MODEL,
    AI_ANALYSIS_BATCH_SIZE,
    ERROR_DETECTION_SAMPLE_RATE,
    ERROR_THRESHOLDS
)


class ConversationAnalyzer:
    """
    Analyzes conversations using Google Gemini API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize conversation analyzer with Google Gemini API.

        Args:
            api_key: Google API key (uses env var if not provided)
        """
        self.api_key = api_key or GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY environment variable."
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(AI_MODEL)

        # Configure generation settings for consistent analysis
        self.generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1000,
        }

    def format_conversation(self, messages: List[Dict]) -> str:
        """
        Format conversation messages for Claude analysis.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted conversation string
        """
        formatted_lines = []

        for msg in messages:
            message_data = msg.get('message', {})
            msg_type = message_data.get('type', 'unknown')
            content = message_data.get('content', '')

            if msg_type == 'human':
                formatted_lines.append(f"Cliente: {content}")
            elif msg_type == 'ai':
                formatted_lines.append(f"IA (Juliana): {content}")
            else:
                formatted_lines.append(f"[{msg_type}]: {content}")

        return "\n\n".join(formatted_lines)

    def analyze_conversation(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single conversation using Google Gemini API.

        Args:
            session: Session dictionary with messages

        Returns:
            Analysis results including error detection and quality score
        """
        messages = session.get('messages', [])

        if not messages:
            return {
                'session_id': session.get('id'),
                'analyzed': False,
                'error': 'No messages found',
                'score': 0
            }

        conversation_text = self.format_conversation(messages)

        # Construct analysis prompt
        prompt = f"""Analise esta conversa de suporte de e-commerce entre o cliente e a IA "Juliana" (agente de suporte da Belevita).

CONVERSA:
{conversation_text}

Por favor, analise a conversa e responda:

1. **Resolução**: O problema ou dúvida do cliente foi resolvido satisfatoriamente?
2. **Compreensão**: A IA entendeu corretamente as solicitações do cliente?
3. **Erros**: Houve algum erro, falha técnica ou mal-entendido por parte da IA?
4. **Qualidade**: Qual foi a qualidade geral do atendimento?
5. **Score**: Atribua um score de confiança de ERRO de 0-100:
   - 0-30: Atendimento excelente, sem problemas
   - 31-60: Atendimento razoável, pequenos problemas
   - 61-80: Atendimento problemático, erros significativos
   - 81-100: Atendimento falhou, erros graves

IMPORTANTE: Responda APENAS com um JSON válido no seguinte formato (sem markdown, sem explicações adicionais):

{{
  "resolved": true,
  "understood": true,
  "had_errors": false,
  "error_description": "descrição dos erros encontrados ou 'nenhum'",
  "quality": "excelente",
  "error_score": 15,
  "reasoning": "breve explicação da análise"
}}"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text

            analysis = json.loads(json_text)

            return {
                'session_id': session.get('id'),
                'analyzed': True,
                'score': analysis.get('error_score', 50),
                'resolved': analysis.get('resolved', False),
                'understood': analysis.get('understood', True),
                'had_errors': analysis.get('had_errors', False),
                'error_description': analysis.get('error_description', ''),
                'quality': analysis.get('quality', 'razoável'),
                'reasoning': analysis.get('reasoning', ''),
                'message_count': len(messages)
            }

        except json.JSONDecodeError as e:
            print(f"JSON parsing error for session {session.get('id')}: {e}")
            print(f"Response was: {response_text[:200]}...")
            return {
                'session_id': session.get('id'),
                'analyzed': False,
                'error': f'JSON parsing error: {str(e)}',
                'score': 50  # Default medium score for failures
            }

        except Exception as e:
            print(f"Error analyzing session {session.get('id')}: {e}")
            return {
                'session_id': session.get('id'),
                'analyzed': False,
                'error': str(e),
                'score': 50
            }

    def select_sessions_for_analysis(self, sessions: List[Dict[str, Any]],
                                     error_detection_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Intelligently select sessions for AI analysis.

        Strategy:
        - All high confidence errors from other methods
        - All negative sentiment sessions
        - Sample of medium confidence errors
        - Sample of neutral sessions
        - Random sample of others

        Args:
            sessions: All sessions
            error_detection_results: Results from error_detector.py

        Returns:
            List of sessions to analyze with AI
        """
        sessions_dict = {s['id']: s for s in sessions}
        error_results_dict = {r['session_id']: r for r in error_detection_results['results']}

        selected = []

        # Priority 1: High confidence errors (>70)
        high_confidence = [
            sessions_dict[r['session_id']]
            for r in error_detection_results['results']
            if r['confidence_level'] == 'high' and r['session_id'] in sessions_dict
        ]
        selected.extend(high_confidence)
        print(f"Selected {len(high_confidence)} high confidence error sessions")

        # Priority 2: All negative sentiment
        negative_sentiment = [
            s for s in sessions
            if s.get('analyse_sentimental') == 'Negativo' and s['id'] not in [x['id'] for x in selected]
        ]
        selected.extend(negative_sentiment)
        print(f"Selected {len(negative_sentiment)} negative sentiment sessions")

        # Priority 3: Medium confidence errors (sample 30%)
        medium_confidence = [
            sessions_dict[r['session_id']]
            for r in error_detection_results['results']
            if r['confidence_level'] == 'medium' and r['session_id'] in sessions_dict
            and sessions_dict[r['session_id']]['id'] not in [x['id'] for x in selected]
        ]

        import random
        random.seed(42)  # For reproducibility
        medium_sample_size = int(len(medium_confidence) * 0.3)
        medium_sample = random.sample(medium_confidence, min(medium_sample_size, len(medium_confidence)))
        selected.extend(medium_sample)
        print(f"Selected {len(medium_sample)} medium confidence sessions (30% sample)")

        # Priority 4: Neutral sentiment sessions (sample 10%)
        neutral_sessions = [
            s for s in sessions
            if s.get('analyse_sentimental') == 'Neutro' and s['id'] not in [x['id'] for x in selected]
        ]
        neutral_sample_size = int(len(neutral_sessions) * 0.10)
        neutral_sample = random.sample(neutral_sessions, min(neutral_sample_size, len(neutral_sessions)))
        selected.extend(neutral_sample)
        print(f"Selected {len(neutral_sample)} neutral sentiment sessions (10% sample)")

        # Priority 5: Fill up to target sample rate with random sessions
        target_total = int(len(sessions) * ERROR_DETECTION_SAMPLE_RATE)
        remaining_needed = max(0, target_total - len(selected))

        if remaining_needed > 0:
            remaining_sessions = [
                s for s in sessions
                if s['id'] not in [x['id'] for x in selected]
            ]
            random_sample = random.sample(remaining_sessions, min(remaining_needed, len(remaining_sessions)))
            selected.extend(random_sample)
            print(f"Selected {len(random_sample)} additional random sessions")

        print(f"Total sessions selected for AI analysis: {len(selected)} ({len(selected)/len(sessions)*100:.1f}%)")

        return selected

    def analyze_sessions_parallel(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple sessions in parallel using ThreadPoolExecutor.

        Args:
            sessions: List of sessions to analyze

        Returns:
            List of analysis results
        """
        results = []

        print(f"Analyzing {len(sessions)} conversations with Google Gemini API...")
        print(f"Using model: {AI_MODEL}")
        print(f"Batch size: {AI_ANALYSIS_BATCH_SIZE}")

        with ThreadPoolExecutor(max_workers=AI_ANALYSIS_BATCH_SIZE) as executor:
            futures = {executor.submit(self.analyze_conversation, session): session for session in sessions}

            for future in tqdm(as_completed(futures), total=len(sessions), desc="Analyzing"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    session = futures[future]
                    print(f"Error analyzing session {session.get('id')}: {e}")
                    results.append({
                        'session_id': session.get('id'),
                        'analyzed': False,
                        'error': str(e),
                        'score': 50
                    })

        successfully_analyzed = sum(1 for r in results if r.get('analyzed', False))
        print(f"Successfully analyzed: {successfully_analyzed}/{len(results)}")

        return results


if __name__ == "__main__":
    print("Conversation Analyzer for Belevita ROI Dashboard")
    print("=" * 50)
    print("Using Google Gemini 2.0 Flash for AI analysis")
    print("This module is meant to be imported and used with extracted data.")
    print("Run generate_report.py to analyze conversations and generate the dashboard.")
