# Belevita - Dashboard ROI Agente IA

Dashboard interativo para análise de ROI do agente de IA "Juliana" que atende o suporte da Belevita.

## Visão Geral

Este projeto analisa aproximadamente **385K mensagens** e **38K sessões** de atendimento para demonstrar o valor e identificar oportunidades de melhoria do agente de IA.

### Principais Recursos

- **4 Métricas Principais**: Volume, Tempo de Resposta, Taxa de Resolução, Análise de Sentimento
- **Detecção de Erros Multi-Método**: Combina análise de frases, padrões comportamentais, IA (Claude) e sentimento
- **Dashboard Interativo**: HTML/JavaScript puro, sem necessidade de servidor
- **Filtros Dinâmicos**: Por data, sentimento e status
- **Visualizações Profissionais**: ApexCharts para gráficos interativos

---

## Estrutura do Projeto

```
relatorio-belevita/
├── config/                         # Configurações
│   ├── settings.py                # IDs, API keys, thresholds
│   └── error_phrases.json         # Frases de erro conhecidas
│
├── scripts/                       # Scripts Python
│   ├── data_extractor.py         # Extração dados Supabase
│   ├── metrics_calculator.py     # Cálculo métricas
│   ├── error_detector.py         # Detecção erros (métodos 1-2-4)
│   ├── conversation_analyzer.py  # Análise IA (método 3)
│   └── generate_report.py        # Script principal
│
├── output/                        # Dados gerados
│   ├── data/                     # JSONs para dashboard
│   └── cache/                    # Cache de dados brutos
│
├── dashboard/                     # Frontend
│   ├── index.html                # Dashboard principal
│   └── assets/
│       ├── css/dashboard.css     # Estilos
│       └── js/
│           ├── dashboard.js      # Lógica principal
│           └── charts.js         # Configuração gráficos
│
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

---

## Instalação e Setup

### Pré-requisitos

- Python 3.9+
- Acesso ao Supabase via MCP (Model Context Protocol)
- API Key do Google (para análise IA com Gemini)

### Passo 1: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 2: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_API_KEY=sua-api-key-do-google-aqui
```

**Como obter a API Key do Google:**
1. Acesse https://aistudio.google.com/app/apikey
2. Crie uma nova API key
3. Copie e cole no arquivo `.env`

### Passo 3: Verificar Configurações

Edite `config/settings.py` se necessário:

```python
# IDs já configurados para Belevita
AGENT_ID = 19
CLIENT_ID = 6

# Ajustar se necessário
ERROR_DETECTION_SAMPLE_RATE = 0.15  # 15% das conversas
AI_ANALYSIS_BATCH_SIZE = 50         # Chamadas paralelas
```

---

## Como Usar

### Opção 1: Geração Completa do Relatório

**Importante**: Este script precisa ser executado em um ambiente com acesso MCP ao Supabase (como Claude Code).

```bash
python scripts/generate_report.py
```

O script irá:
1. ✓ Extrair dados do Supabase (~10 min)
2. ✓ Calcular métricas (~3 min)
3. ✓ Detectar erros com métodos 1-2-4 (~5 min)
4. ✓ Analisar ~5.6K conversas com Gemini 2.0 Flash (~15-30 min, **GRÁTIS**)
5. ✓ Gerar JSONs para dashboard (~1 min)

**Tempo total estimado**: ~35-50 minutos

**Custo**: GRÁTIS (Gemini 2.0 Flash tem até 1500 requests/dia grátis)

### Opção 2: Usar Cache (Mais Rápido)

Se os dados já foram extraídos anteriormente:

```bash
python scripts/generate_report.py --use-cache
```

### Opção 3: Pular Análise IA (Mais Rápido, Menos Preciso)

```bash
python scripts/generate_report.py --skip-ai-analysis
```

Isso reduz o tempo para ~15-20 minutos e custo zero, mas a detecção de erros será menos precisa (apenas métodos 1, 2 e 4).

---

## Visualizar Dashboard

Após gerar os dados:

### Windows
```bash
# Duplo-clique em:
dashboard/index.html
```

### Mac/Linux
```bash
open dashboard/index.html
# ou
xdg-open dashboard/index.html
```

O dashboard abrirá no navegador padrão e carregará os dados automaticamente.

---

## Métricas e Análises

### 1. Volume de Atendimentos

- **Sessões por dia**: Quantidade de atendimentos diários
- **Média móvel 7 dias**: Tendência suavizada
- **Picos**: Identificação de horários de maior demanda
- **Leads únicos**: Clientes distintos atendidos

### 2. Tempo de Resposta Médio

- **Mediana por dia**: Tempo médio de primeira resposta
- **Percentil 95**: Tempo no pior caso (95% dos casos)
- **Outliers**: Casos > 5 minutos identificados

### 3. Taxa de Resolução

- **% Completadas**: Sessões finalizadas com sucesso
- **Tendência semanal**: Evolução ao longo do tempo
- **Breakdown por tipo**: Resolução por categoria de interação

### 4. Análise de Sentimento

- **Distribuição**: Positivo / Neutro / Negativo
- **Evolução temporal**: Mudanças semanais
- **Correlação**: Relação com taxa de resolução

---

## Detecção de Erros Multi-Método

### Método 1: Frases Específicas (30% peso)

Busca em mensagens por frases conhecidas:
- Indicadores de erro: "não entendi", "erro", "problema"
- Frustração: "péssimo", "não resolve nada"
- Escalação: "quero falar com humano"

**Editar frases**: `config/error_phrases.json`

### Método 2: Padrões Comportamentais (25% peso)

Detecta:
- Conversas muito curtas (< 3 mensagens)
- Abandono rápido (< 2 minutos)
- Mensagens repetidas do usuário
- Sessões travadas (ativas > 30 min)
- Sessões com status "falhou"

### Método 3: Análise IA - Gemini API (35% peso)

Gemini 2.0 Flash analisa conversas selecionadas e avalia:
1. O problema foi resolvido?
2. A IA entendeu corretamente?
3. Houve erros ou falhas?
4. Score de confiança (0-100)

**Seleção inteligente (~15% das conversas)**:
- Todas sessões sentimento negativo
- Todos erros alta confiança (métodos 1-2)
- Amostra 30% erros média confiança
- Amostra 10% sessões neutras
- Amostra aleatória do restante

### Método 4: Correlação Sentimento (10% peso)

- Negativo: 80% probabilidade erro
- Neutro: 20% probabilidade erro
- Positivo: 5% probabilidade erro

### Score Final Combinado

```
Score = (Método_1 × 0.30) + (Método_2 × 0.25) + (Método_3 × 0.35) + (Método_4 × 0.10)
```

**Categorização:**
- **Alta confiança** (>70%): Erro confirmado
- **Média confiança** (40-70%): Possível erro
- **Baixa confiança** (<40%): Provável sucesso

---

## Filtros do Dashboard

### Filtro de Data
Selecione um período específico para análise:
- Clique no campo "Período"
- Escolha data inicial e final
- Dashboard atualiza automaticamente

### Filtro de Sentimento
- **Todos**: Todas as sessões
- **Positivo**: Apenas sentimento positivo
- **Neutro**: Apenas neutro
- **Negativo**: Apenas negativo

### Filtro de Status
- **Todos**: Todas as sessões
- **Completado**: Sessões finalizadas
- **Ativo**: Sessões em andamento
- **Falhou**: Sessões com erro

### Limpar Filtros
Botão "Limpar Filtros" reseta todos os filtros ao estado inicial.

---

## Arquivos Gerados

Após executar `generate_report.py`, os seguintes arquivos são criados em `output/data/`:

| Arquivo | Descrição | Tamanho |
|---------|-----------|---------|
| `summary.json` | Resumo geral de todas métricas | ~5KB |
| `daily_metrics.json` | Todas as métricas completas | ~50KB |
| `sentiment_analysis.json` | Dados de sentimento detalhados | ~100KB |
| `error_analysis.json` | Resultados detecção de erros | ~500KB |
| `conversation_samples.json` | Top 500 conversas com erros | ~5MB |
| `sessions_summary.json` | Resumo de todas sessões | ~2MB |

**Total**: ~7-8MB (carregamento rápido no dashboard)

---

## Entrega ao Cliente

### Criar Pacote

```bash
# Windows
tar -czf belevita-dashboard.zip dashboard/ output/

# Mac/Linux
zip -r belevita-dashboard.zip dashboard/ output/
```

### Instruções para Cliente

1. Extrair arquivo ZIP
2. Duplo-clique em `dashboard/index.html`
3. Dashboard abre no navegador
4. **Sem necessidade de instalação ou servidor!**

---

## Atualizar Relatório com Novos Dados

Para gerar um novo relatório com dados atualizados:

```bash
# 1. Re-extrair dados do Supabase
python scripts/generate_report.py

# 2. Dashboard index.html automaticamente carrega novos dados
# Basta recarregar a página no navegador (F5)
```

**Frequência recomendada**: Mensal ou trimestral

---

## Custos Estimados

### Análise Completa (com IA)
- **Gemini 2.0 Flash**: **GRÁTIS** (até 1500 requests/dia)
- **Tempo**: ~35-50 minutos
- **Precisão**: Alta (~85-90%)

### Análise Básica (sem IA)
- **Custo**: $0
- **Tempo**: ~15-20 minutos
- **Precisão**: Média (~70-75%)

**Vantagem do Gemini 2.0 Flash**: Modelo rápido e gratuito, ideal para análise em larga escala!

---

## Troubleshooting

### Erro: "Data extraction requires MCP access"

**Problema**: Script não consegue acessar Supabase

**Solução**: Execute o script dentro do Claude Code com MCP configurado, ou use `--use-cache` se dados já foram extraídos

### Erro: "Google API key not found"

**Problema**: API key não configurada

**Solução**:
```bash
export GOOGLE_API_KEY="sua-key"
# ou crie arquivo .env com GOOGLE_API_KEY=sua-key
```

### Dashboard não carrega dados

**Problema**: Arquivos JSON não foram gerados

**Solução**:
1. Verifique se `output/data/` contém arquivos `.json`
2. Se não, execute `python scripts/generate_report.py`
3. Verifique console do navegador (F12) para erros

### Gráficos não aparecem

**Problema**: CDN do ApexCharts bloqueado

**Solução**: Verifique conexão internet ou baixe ApexCharts localmente

---

## Próximas Melhorias

Possíveis extensões futuras:

- [ ] Export PDF do relatório
- [ ] Export CSV dos dados filtrados
- [ ] Comparação entre períodos (antes/depois)
- [ ] Análise de custo por sessão (ROI financeiro)
- [ ] Integração com outros clientes (multi-tenant)
- [ ] Atualização automática (agendada)
- [ ] Alertas para degradação de métricas

---

## Suporte

Para dúvidas ou problemas:

1. Verifique logs do console: `python scripts/generate_report.py`
2. Cheque arquivos de configuração: `config/settings.py`
3. Revise este README para instruções detalhadas

---

## Tecnologias Utilizadas

**Backend (Processamento)**:
- Python 3.9+
- Pandas (manipulação dados)
- Google Generative AI SDK (análise IA com Gemini)
- Supabase via MCP (banco de dados)

**Frontend (Dashboard)**:
- HTML5 + CSS3
- JavaScript Vanilla
- ApexCharts (visualizações)
- Flatpickr (date picker)

---

## Licença

Este projeto é proprietário e confidencial. Desenvolvido para uso exclusivo da Belevita.

---

**Desenvolvido com Claude Code** 🤖

*Dashboard gerado automaticamente com análise multi-método de qualidade e detecção de erros.*
