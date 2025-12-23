#!/usr/bin/env python3
"""
Metrics Extractor for Belevita ROI Dashboard
Extracts real data from Supabase and generates metrics.json for the frontend.
"""

import json
import os
import sys
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from supabase import create_client, Client
from tqdm import tqdm

from config.settings import AGENT_ID, CLIENT_ID, SUPABASE_PROJECT_REF

# Load environment variables
load_dotenv()

# Dados fornecidos pelo cliente
TOTAL_PEDIDOS = 35165
TICKET_MEDIO = 179
CUSTO_HORA_ATENDENTE = 10.22

# Keywords para detecção
KEYWORDS = {
    "rastreio": ["onde está", "rastrear", "rastreio", "rastreamento", "quando chega", "meu pedido", "cadê meu pedido", "status do pedido"],
    "troca": ["trocar", "troca", "devolver", "devolução", "não serviu", "tamanho errado"],
    "cancelamento": ["cancelar", "cancelamento", "desistir", "reembolso", "estorno"],
    "duvida": ["como funciona", "dúvida", "como faço", "me ajuda", "pode me ajudar"],
    
    # Sentimento
    "positivo": ["obrigado", "obrigada", "perfeito", "ótimo", "excelente", "top", "maravilhoso", "amei"],
    "negativo": ["absurdo", "ridículo", "péssimo", "horrível", "frustrado", "não aguento", "reclamar", "nunca mais"],
    
    # Produtos
    "calcados": ["tênis", "sapato", "sandália", "chinelo", "bota", "sapatilha", "calçado"],
    "calcas": ["calça", "jeans", "legging", "shorts", "bermuda"],
    "blusas": ["blusa", "camiseta", "camisa", "cropped", "top", "regata"],
    "moda_intima": ["sutiã", "calcinha", "cueca", "lingerie", "pijama"],
    "acessorios": ["bolsa", "cinto", "colar", "brinco", "pulseira", "óculos"],
    
    # Risco
    "procon": ["procon", "consumidor", "juridico", "advogado"],
    "reclame_aqui": ["reclame aqui", "reclameaqui"],
    "golpe": ["golpe", "fraude", "enganado", "mentira"],
    "estorno": ["estorno", "chargeback", "contestar", "banco"],
    
    # Vazamento de Tool/Prompt (mensagens DA IA)
    "tool_leak": [
        "<tool_code>", "print(default_api", "tool_call", "send_notification",
        "ENVIE A RESPOSTA", "O cliente fez ameaça", "EU USEI A TOOL",
        "sentimental='", "type_interaction=", "score='", "resume='",
        "Finalizar_atendimento", "default_api.", "<tool>", "</tool>",
        "Vou falar que avisei", "O texto tá natural"
    ],
    
    # Cliente percebeu que é IA (mensagens DO CLIENTE)
    "percebeu_ia": [
        "robô", "robo", "bot", "automático", "automatico", "máquina", "maquina",
        "inteligência artificial", "inteligencia artificial", "isso é ia", "isso e ia",
        "quero falar com humano", "atendente humano", "pessoa de verdade",
        "não é gente", "nao e gente", "chatbot", "resposta automática",
        "você é um robô", "voce e um robo", "falar com alguém de verdade"
    ],
}


class MetricsExtractor:
    """Extracts metrics from Supabase for the ROI Dashboard."""

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
        
        # Initialize counters
        self.reset_counters()

    def reset_counters(self):
        """Reset all counters."""
        self.total_conversas = 0
        self.total_mensagens = 0
        self.intencoes = Counter()
        self.sentimentos = Counter()
        self.produtos = Counter()
        self.riscos = Counter()
        self.mensagens_por_hora = Counter()
        self.mensagens_por_mes = Counter()
        self.problemas_detectados = 0
        
        # Novos contadores para erros de IA
        self.tool_leaks = 0
        self.tool_leak_examples = []
        self.percebeu_ia = 0
        self.percebeu_ia_examples = []

    def fetch_chat_histories(self, limit: int = None) -> List[Dict]:
        """Fetch all chat histories with pagination."""
        print("\nFetching chat histories...")
        all_messages = []
        offset = 0
        batch_size = 1000
        
        while True:
            try:
                response = self.client.table("n8n_chat_histories").select(
                    "id, session_id, message"
                ).order("id").range(offset, offset + batch_size - 1).execute()
                
                batch = response.data
                if not batch:
                    break
                
                all_messages.extend(batch)
                offset += batch_size
                print(f"  Fetched {len(all_messages)} messages...")
                
                if limit and len(all_messages) >= limit:
                    break
                    
            except Exception as e:
                print(f"  Error at offset {offset}: {e}")
                offset += batch_size
                continue
        
        print(f"[OK] Total: {len(all_messages)} messages")
        return all_messages

    def fetch_agent_sessions(self) -> List[Dict]:
        """Fetch agent sessions for time-based analysis."""
        print("\nFetching agent sessions...")
        all_sessions = []
        offset = 0
        batch_size = 1000
        
        while True:
            try:
                response = self.client.table("agent_sessions").select(
                    "id, started_at, ended_at, analyse_sentimental"
                ).order("id").range(offset, offset + batch_size - 1).execute()
                
                batch = response.data
                if not batch:
                    break
                
                all_sessions.extend(batch)
                offset += batch_size
                
            except Exception as e:
                print(f"  Error at offset {offset}: {e}")
                break
        
        print(f"[OK] Total: {len(all_sessions)} sessions")
        return all_sessions

    def detect_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if any keyword is present in the text."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    def analyze_message(self, message_content: str) -> Dict[str, Any]:
        """Analyze a single message for intents, sentiment, products, risks."""
        results = {
            "intencao": None,
            "sentimento": "neutro",
            "produtos": [],
            "riscos": [],
        }
        
        # Detect intention
        for intencao in ["rastreio", "troca", "cancelamento", "duvida"]:
            if self.detect_keywords(message_content, KEYWORDS[intencao]):
                results["intencao"] = intencao
                break
        
        # Detect sentiment
        if self.detect_keywords(message_content, KEYWORDS["positivo"]):
            results["sentimento"] = "positivo"
        elif self.detect_keywords(message_content, KEYWORDS["negativo"]):
            results["sentimento"] = "negativo"
        
        # Detect products
        for produto in ["calcados", "calcas", "blusas", "moda_intima", "acessorios"]:
            if self.detect_keywords(message_content, KEYWORDS[produto]):
                results["produtos"].append(produto)
        
        # Detect risks
        for risco in ["procon", "reclame_aqui", "golpe", "estorno"]:
            if self.detect_keywords(message_content, KEYWORDS[risco]):
                results["riscos"].append(risco)
        
        return results

    def process_messages(self, messages: List[Dict]) -> Dict[str, Any]:
        """Process all messages and aggregate metrics."""
        print("\nProcessing messages...")
        
        conversations = defaultdict(list)
        
        # Group by session
        for msg in tqdm(messages, desc="Grouping"):
            session_id = msg.get("session_id")
            if session_id:
                conversations[session_id].append(msg)
        
        self.total_conversas = len(conversations)
        self.total_mensagens = len(messages)
        
        # Analyze each conversation
        for session_id, msgs in tqdm(conversations.items(), desc="Analyzing"):
            human_text = ""
            ai_text = ""
            
            for msg in msgs:
                message_data = msg.get("message", {})
                if isinstance(message_data, dict):
                    content = message_data.get("content", "")
                    msg_type = message_data.get("type", "")
                    
                    if msg_type == "human" and content:
                        human_text += " " + content
                    elif msg_type == "ai" and content:
                        ai_text += " " + content
            
            # Detectar vazamento de tool (nas mensagens DA IA)
            if ai_text and self.detect_keywords(ai_text, KEYWORDS["tool_leak"]):
                self.tool_leaks += 1
                if len(self.tool_leak_examples) < 10:  # Guardar até 10 exemplos
                    self.tool_leak_examples.append({
                        "session_id": session_id,
                        "preview": ai_text[:200]
                    })
            
            # Detectar cliente percebendo IA (nas mensagens DO CLIENTE)
            if human_text and self.detect_keywords(human_text, KEYWORDS["percebeu_ia"]):
                self.percebeu_ia += 1
                if len(self.percebeu_ia_examples) < 10:
                    self.percebeu_ia_examples.append({
                        "session_id": session_id,
                        "preview": human_text[:200]
                    })
            
            # Análise normal (intenções, sentimento, produtos, riscos)
            if human_text:
                analysis = self.analyze_message(human_text)
                
                if analysis["intencao"]:
                    self.intencoes[analysis["intencao"]] += 1
                else:
                    self.intencoes["outros"] += 1
                
                self.sentimentos[analysis["sentimento"]] += 1
                
                for produto in analysis["produtos"]:
                    self.produtos[produto] += 1
                
                for risco in analysis["riscos"]:
                    self.riscos[risco] += 1
                    self.problemas_detectados += 1
        
        print(f"[OK] Processed {self.total_conversas} conversations")

    def process_sessions(self, sessions: List[Dict]):
        """Process sessions for time-based metrics."""
        print("\nProcessing sessions for time analysis...")
        
        for session in tqdm(sessions, desc="Sessions"):
            started_at = session.get("started_at")
            if started_at:
                try:
                    dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    self.mensagens_por_hora[dt.hour] += 1
                    self.mensagens_por_mes[dt.strftime("%b")] += 1
                except:
                    pass
        
        print("[OK] Time analysis complete")

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate all metrics for the dashboard."""
        print("\nCalculating metrics...")
        
        # Taxa de contato
        taxa_contato = round((self.total_conversas / TOTAL_PEDIDOS) * 100, 1) if TOTAL_PEDIDOS else 0
        
        # Taxa de resolução (estimada - conversas sem menção de problema)
        taxa_resolucao = round(((self.total_conversas - self.problemas_detectados) / self.total_conversas) * 100, 1) if self.total_conversas else 0
        
        # Economia (estimativa: 10 min por conversa)
        horas_economizadas = round(self.total_conversas * 10 / 60)
        economia_reais = round(horas_economizadas * CUSTO_HORA_ATENDENTE)
        
        # Revenue at risk
        conversas_criticas = sum(self.riscos.values())
        revenue_at_risk = conversas_criticas * TICKET_MEDIO
        
        # WISMO (rastreio)
        wismo_pct = round((self.intencoes.get("rastreio", 0) / self.total_conversas) * 100, 1) if self.total_conversas else 0
        
        metrics = {
            "kpis": {
                "totalConversas": self.total_conversas,
                "totalPedidos": TOTAL_PEDIDOS,
                "taxaContato": taxa_contato,
                "taxaResolucaoIA": min(taxa_resolucao, 95),  # Cap at 95%
                "ticketMedio": TICKET_MEDIO,
                "custoHoraAtendente": CUSTO_HORA_ATENDENTE,
            },
            "financeiro": {
                "conversasCriticas": conversas_criticas,
                "revenueAtRisk": revenue_at_risk,
                "horasEconomizadas": horas_economizadas,
                "economiaReais": economia_reais,
            },
            "sentimento": [
                {"tipo": "Positivo", "quantidade": self.sentimentos.get("positivo", 0), "fill": "#3b82f6"},
                {"tipo": "Neutro", "quantidade": self.sentimentos.get("neutro", 0), "fill": "#1d8ecf"},
                {"tipo": "Negativo", "quantidade": self.sentimentos.get("negativo", 0), "fill": "#0f13e4"},
            ],
            "intencoes": [
                {"name": "Rastreio", "value": self.intencoes.get("rastreio", 0)},
                {"name": "Troca", "value": self.intencoes.get("troca", 0)},
                {"name": "Dúvida", "value": self.intencoes.get("duvida", 0)},
                {"name": "Cancelamento", "value": self.intencoes.get("cancelamento", 0)},
                {"name": "Outros", "value": self.intencoes.get("outros", 0)},
            ],
            "produtosProblemas": [
                {"categoria": "Calçados", "reclamacoes": self.produtos.get("calcados", 0)},
                {"categoria": "Calças", "reclamacoes": self.produtos.get("calcas", 0)},
                {"categoria": "Moda Íntima", "reclamacoes": self.produtos.get("moda_intima", 0)},
                {"categoria": "Acessórios", "reclamacoes": self.produtos.get("acessorios", 0)},
                {"categoria": "Blusas", "reclamacoes": self.produtos.get("blusas", 0)},
            ],
            "risco": [
                {"tipo": "Estorno", "quantidade": self.riscos.get("estorno", 0)},
                {"tipo": "PROCON", "quantidade": self.riscos.get("procon", 0)},
                {"tipo": "Reclame Aqui", "quantidade": self.riscos.get("reclame_aqui", 0)},
                {"tipo": "Golpe", "quantidade": self.riscos.get("golpe", 0)},
            ],
            "volumeMensal": [
                {"mes": mes, "atendimentos": count}
                for mes, count in sorted(self.mensagens_por_mes.items(), key=lambda x: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"].index(x[0]) if x[0] in ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"] else 99)
            ] or [
                {"mes": "Jan", "atendimentos": 0},
                {"mes": "Fev", "atendimentos": 0},
                {"mes": "Mar", "atendimentos": 0},
                {"mes": "Abr", "atendimentos": 0},
                {"mes": "Mai", "atendimentos": 0},
                {"mes": "Jun", "atendimentos": 0},
            ],
            "porHora": [
                {"hora": f"{h:02d}h", "quantidade": self.mensagens_por_hora.get(h, 0)}
                for h in range(8, 22)
            ],
            "errosIA": {
                "toolLeaks": self.tool_leaks,
                "toolLeakExamples": self.tool_leak_examples,
                "percebeuIA": self.percebeu_ia,
                "percebeuIAExamples": self.percebeu_ia_examples,
            },
            "wismo": wismo_pct,
            "geradoEm": datetime.now().isoformat(),
        }
        
        # Sort products by reclamacoes
        metrics["produtosProblemas"].sort(key=lambda x: x["reclamacoes"], reverse=True)
        
        # Sort intencoes by value
        metrics["intencoes"].sort(key=lambda x: x["value"], reverse=True)
        
        print("[OK] Metrics calculated")
        return metrics

    def save_metrics(self, metrics: Dict[str, Any], output_path: str):
        """Save metrics to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Metrics saved to {output_path}")

    def run(self, output_path: str = "frontend/lib/metrics.json"):
        """Run the full extraction and calculation pipeline."""
        print("="*60)
        print("BELEVITA METRICS EXTRACTOR")
        print("="*60)
        
        # Fetch data
        messages = self.fetch_chat_histories()
        sessions = self.fetch_agent_sessions()
        
        # Process
        self.process_messages(messages)
        self.process_sessions(sessions)
        
        # Calculate
        metrics = self.calculate_metrics()
        
        # Save
        self.save_metrics(metrics, output_path)
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total Conversas: {self.total_conversas:,}")
        print(f"Total Mensagens: {self.total_mensagens:,}")
        print(f"Taxa de Contato: {metrics['kpis']['taxaContato']}%")
        print(f"WISMO: {metrics['wismo']}%")
        print(f"Economia: R$ {metrics['financeiro']['economiaReais']:,}")
        print(f"Revenue at Risk: R$ {metrics['financeiro']['revenueAtRisk']:,}")
        print("-"*60)
        print(f"Vazamentos de Tool: {self.tool_leaks}")
        print(f"Cliente Percebeu IA: {self.percebeu_ia}")
        print("="*60)
        
        return metrics


if __name__ == "__main__":
    extractor = MetricsExtractor()
    extractor.run()
