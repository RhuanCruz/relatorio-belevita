"use client"

import Image from "next/image"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Area, AreaChart, CartesianGrid, Cell, Label } from "recharts"
import { MessageSquare, Bot, DollarSign, ShieldCheck, AlertTriangle, Clock, TrendingUp, Package, HelpCircle, Users } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Separator } from "@/components/ui/separator"
import { metricsData } from "@/lib/data"

// Opus Hub Color Palette
const COLORS = ["#00f2fe", "#4facfe", "#6a11cb", "#8b5cf6", "#06b6d4"]

const chartConfig = {
  atendimentos: { label: "Atendimentos", color: "#00f2fe" },
  quantidade: { label: "Quantidade", color: "#4facfe" },
  reclamacoes: { label: "Reclamações", color: "#6a11cb" },
  value: { label: "Quantidade", color: "#00f2fe" },
} satisfies ChartConfig

const sentimentoConfig = {
  quantidade: { label: "Quantidade" },
  Positivo: { label: "Positivo", color: "#00f2fe" },
  Neutro: { label: "Neutro", color: "#4facfe" },
  Negativo: { label: "Negativo", color: "#6a11cb" },
} satisfies ChartConfig

// Componente de ajuda reutilizável
function HelpTooltip({ text }: { text: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <HelpCircle className="h-4 w-4 text-[#b0b0b0] cursor-help hover:text-[#00f2fe] transition-colors" />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-xs text-sm bg-[#1a1a1a] border-[#2a2a2a] text-[#f0f0f0]">
        <p>{text}</p>
      </TooltipContent>
    </Tooltip>
  )
}

export default function Dashboard() {
  return (
    <TooltipProvider>
      <main className="min-h-screen opus-bg-gradient">
        <div className="container mx-auto max-w-6xl px-8 py-8">
          {/* Header with Logo */}
          <header className="mb-12">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <Image
                  src="/opus-logo.png"
                  alt="Opus Hub"
                  width={140}
                  height={40}
                  className="opus-glow"
                />
              </div>
              <div className="opus-pill">
                Powered by AI
              </div>
            </div>
            <div className="border-l-4 pl-4" style={{ borderImage: 'linear-gradient(180deg, #00f2fe, #6a11cb) 1' }}>
              <h1 className="text-3xl font-semibold text-[#f0f0f0]">Relatório Belevita - 2025</h1>
              <p className="text-[#b0b0b0] mt-1">Análise de performance do agente IA</p>
            </div>
          </header>

          {/* KPI Cards - Linha 1 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Taxa de Contato</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Percentual de pedidos que geraram um chamado no suporte. Calculado como: (Total de Conversas ÷ Total de Pedidos) × 100. Meta ideal: abaixo de 30%." />
                  <MessageSquare className="h-4 w-4 text-[#00f2fe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold opus-gradient-text">{metricsData.kpis.taxaContato}%</div>
                <p className="text-xs text-[#b0b0b0]">{metricsData.kpis.totalConversas.toLocaleString()} chamados / {metricsData.kpis.totalPedidos.toLocaleString()} pedidos</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Resolução IA</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Percentual de conversas resolvidas 100% pela IA, sem necessidade de transbordo para atendente humano." />
                  <Bot className="h-4 w-4 text-[#00f2fe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#00f2fe]">{metricsData.kpis.taxaResolucaoIA}%</div>
                <p className="text-xs text-[#b0b0b0]">sem escalação humana</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Economia Gerada</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text={`Valor economizado com atendimento automatizado. Calculado como: Horas Economizadas × Custo/Hora (R$ ${metricsData.kpis.custoHoraAtendente}). Estimativa de 10 minutos por conversa.`} />
                  <DollarSign className="h-4 w-4 text-[#00f2fe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#00f2fe]">R$ {metricsData.financeiro.economiaReais.toLocaleString()}</div>
                <p className="text-xs text-[#b0b0b0]">{metricsData.financeiro.horasEconomizadas.toLocaleString()} horas poupadas</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Revenue Protegido</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text={`Valor em pedidos que a IA ajudou a reter, evitando cancelamentos. Calculado como: Conversas Críticas × Ticket Médio (R$ ${metricsData.kpis.ticketMedio}).`} />
                  <ShieldCheck className="h-4 w-4 text-[#00f2fe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#f0f0f0]">R$ {(metricsData.financeiro.revenueAtRisk / 1000).toFixed(0)}K</div>
                <p className="text-xs text-[#b0b0b0]">{metricsData.financeiro.conversasCriticas.toLocaleString()} conversas críticas</p>
              </CardContent>
            </Card>
          </section>

          {/* KPI Cards - Linha 2 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Total Conversas</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Número total de sessões de chat únicas registradas no período analisado." />
                  <Users className="h-4 w-4 text-[#4facfe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#f0f0f0]">{metricsData.kpis.totalConversas.toLocaleString()}</div>
                <p className="text-xs text-[#b0b0b0]">no período analisado</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Ticket Médio</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Valor médio de cada pedido na loja. Usado para calcular Revenue at Risk e outras métricas financeiras." />
                  <Package className="h-4 w-4 text-[#4facfe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#f0f0f0]">R$ {metricsData.kpis.ticketMedio}</div>
                <p className="text-xs text-[#b0b0b0]">valor médio por pedido</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#00f2fe]/30 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">WISMO</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="'Where Is My Order' - Percentual de chamados sobre rastreamento de pedido. Detectado por palavras-chave como 'onde está', 'rastreio', 'quando chega'." />
                  <Clock className="h-4 w-4 text-[#4facfe]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#f0f0f0]">{metricsData.wismo}%</div>
                <p className="text-xs text-[#b0b0b0]">chamados sobre rastreio</p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#2a2a2a] hover:border-[#6a11cb]/50 transition-all">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Alertas de Risco</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Menções críticas que indicam risco de perda de cliente. Inclui: PROCON, Reclame Aqui, acusações de golpe e pedidos de estorno/chargeback." />
                  <AlertTriangle className="h-4 w-4 text-[#ef4444]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#ef4444]">{metricsData.risco.reduce((a, b) => a + b.quantidade, 0)}</div>
                <p className="text-xs text-[#b0b0b0]">menções críticas detectadas</p>
              </CardContent>
            </Card>
          </section>

          {/* Erros de IA - Seção Crítica */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
            <Card className="bg-[#151515] border-[#ef4444]/30">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Vazamento de Tool</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Mensagens onde a IA mostrou código interno, como <tool_code>, print(default_api...), ou instruções internas. Isso revela que é uma IA e não um humano." />
                  <AlertTriangle className="h-4 w-4 text-[#ef4444]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#ef4444]">
                  {((metricsData.errosIA?.toolLeaks || 0) / metricsData.kpis.totalConversas * 100).toFixed(2)}%
                </div>
                <p className="text-xs text-[#b0b0b0]">
                  {metricsData.errosIA?.toolLeaks || 0} conversas com vazamento
                </p>
              </CardContent>
            </Card>

            <Card className="bg-[#151515] border-[#f97316]/30">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#f0f0f0]">Cliente Percebeu IA</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Conversas onde o cliente mencionou que percebeu ser uma IA, usando termos como 'robô', 'bot', 'automático', 'quero falar com humano'." />
                  <Bot className="h-4 w-4 text-[#f97316]" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#f97316]">
                  {((metricsData.errosIA?.percebeuIA || 0) / metricsData.kpis.totalConversas * 100).toFixed(1)}%
                </div>
                <p className="text-xs text-[#b0b0b0]">
                  {metricsData.errosIA?.percebeuIA || 0} clientes notaram
                </p>
              </CardContent>
            </Card>
          </section>

          <Separator className="mb-12 bg-[#2a2a2a]" />

          {/* Grid Charts - Linha 1 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {/* Intenções */}
            <Card className="bg-[#151515] border-[#2a2a2a]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-[#f0f0f0]">Motivos de Contato</CardTitle>
                  <HelpTooltip text="Classificação automática das intenções dos clientes. Detectado por palavras-chave: Rastreio (onde está, rastrear), Troca (trocar, devolver), Cancelamento (cancelar), Dúvida (como funciona)." />
                </div>
                <CardDescription className="text-[#b0b0b0]">Distribuição por intenção</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.intencoes} layout="vertical" accessibilityLayer>
                    <XAxis type="number" stroke="#b0b0b0" />
                    <YAxis dataKey="name" type="category" width={100} stroke="#b0b0b0" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="value" radius={4}>
                      {metricsData.intencoes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Produtos */}
            <Card className="bg-[#151515] border-[#2a2a2a]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-[#f0f0f0]">Produtos com Problemas</CardTitle>
                  <HelpTooltip text="Categorias de produtos mais mencionadas em conversas com indicadores de problema (reclamação, defeito, troca). Quanto maior a barra, maior a dor de cabeça operacional." />
                </div>
                <CardDescription className="text-[#b0b0b0]">Categorias mais reclamadas</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.produtosProblemas} accessibilityLayer>
                    <XAxis dataKey="categoria" angle={-45} textAnchor="end" height={80} stroke="#b0b0b0" />
                    <YAxis stroke="#b0b0b0" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="reclamacoes" fill="#6a11cb" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Sentimento */}
            <Card className="bg-[#151515] border-[#2a2a2a]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-[#f0f0f0]">Sentimento</CardTitle>
                  <HelpTooltip text="Análise de sentimento das conversas baseada em palavras-chave. Positivo (obrigado, ótimo), Neutro (ok, entendi), Negativo (frustrado, absurdo)." />
                </div>
                <CardDescription className="text-[#b0b0b0]">Distribuição geral</CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <ChartContainer config={sentimentoConfig} className="h-[280px] w-full">
                  <PieChart accessibilityLayer>
                    <Pie
                      data={metricsData.sentimento}
                      dataKey="quantidade"
                      nameKey="tipo"
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                    >
                      {metricsData.sentimento.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                      <Label value={`${Math.round((metricsData.sentimento[0].quantidade / metricsData.kpis.totalConversas) * 100)}%`} position="center" className="text-2xl font-bold" fill="#f0f0f0" />
                    </Pie>
                    <ChartTooltip content={<ChartTooltipContent nameKey="tipo" />} />
                    <ChartLegend content={<ChartLegendContent nameKey="tipo" />} />
                  </PieChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </section>

          {/* Grid Charts - Linha 2 */}
          <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
            {/* Volume por Hora */}
            <Card className="bg-[#151515] border-[#2a2a2a]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-[#f0f0f0]">Atendimentos por Hora</CardTitle>
                  <HelpTooltip text="Distribuição de atendimentos ao longo do dia. Útil para identificar horários de pico e calcular economia com atendimento noturno (19h-08h)." />
                </div>
                <CardDescription className="text-[#b0b0b0]">Distribuição ao longo do dia</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.porHora} accessibilityLayer>
                    <XAxis dataKey="hora" stroke="#b0b0b0" />
                    <YAxis stroke="#b0b0b0" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="quantidade" fill="#4facfe" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Termômetro de Risco */}
            <Card className="bg-[#151515] border-[#2a2a2a]">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-[#f0f0f0]">Termômetro de Risco</CardTitle>
                  <HelpTooltip text="Menções críticas que indicam risco legal ou financeiro. PROCON/Reclame Aqui = risco de reputação. Estorno = risco de chargeback. Acompanhe tendências mensais." />
                </div>
                <CardDescription className="text-[#b0b0b0]">Menções críticas detectadas</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.risco} layout="vertical" accessibilityLayer>
                    <XAxis type="number" stroke="#b0b0b0" />
                    <YAxis dataKey="tipo" type="category" width={100} stroke="#b0b0b0" />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="quantidade" fill="#6a11cb" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </section>

          <Separator className="mb-12 bg-[#2a2a2a]" />

          {/* Seção de Resumo */}
          <section className="mb-12">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-xl font-semibold text-[#f0f0f0]">Resumo Executivo</h2>
              <HelpTooltip text="Síntese dos principais insights do período. Ganhos = resultados positivos. Alertas = pontos que requerem atenção. Oportunidades = ações sugeridas." />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-[#151515] border-l-4" style={{ borderLeftColor: '#00f2fe' }}>
                <CardHeader>
                  <CardTitle className="text-[#00f2fe] flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Ganhos
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-[#b0b0b0]">• Economia de <span className="text-[#00f2fe] font-semibold">R$ {metricsData.financeiro.economiaReais.toLocaleString()}</span> em atendimento</p>
                  <p className="text-sm text-[#b0b0b0]">• <span className="text-[#00f2fe] font-semibold">{metricsData.kpis.taxaResolucaoIA}%</span> resolvido pela IA</p>
                  <p className="text-sm text-[#b0b0b0]">• <span className="text-[#00f2fe] font-semibold">R$ {(metricsData.financeiro.revenueAtRisk / 1000).toFixed(0)}K</span> em pedidos protegidos</p>
                </CardContent>
              </Card>

              <Card className="bg-[#151515] border-l-4" style={{ borderLeftColor: '#ef4444' }}>
                <CardHeader>
                  <CardTitle className="text-[#ef4444] flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Alertas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-[#b0b0b0]">• Taxa de contato alta: <span className="text-[#ef4444] font-semibold">{metricsData.kpis.taxaContato}%</span></p>
                  <p className="text-sm text-[#b0b0b0]">• <span className="text-[#ef4444] font-semibold">{metricsData.produtosProblemas[0].reclamacoes}</span> reclamações em Calçados</p>
                  <p className="text-sm text-[#b0b0b0]">• <span className="text-[#ef4444] font-semibold">{metricsData.risco.reduce((a, b) => a + b.quantidade, 0)}</span> menções de risco</p>
                </CardContent>
              </Card>

              <Card className="bg-[#151515] border-l-4" style={{ borderLeftColor: '#6a11cb' }}>
                <CardHeader>
                  <CardTitle className="text-[#6a11cb] flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    Oportunidades
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-[#b0b0b0]">• 40.7% dos chamados são WISMO - automatizar alertas</p>
                  <p className="text-sm text-[#b0b0b0]">• Revisar fornecedor de Calçados</p>
                  <p className="text-sm text-[#b0b0b0]">• Melhorar tabela de medidas</p>
                </CardContent>
              </Card>
            </div>
          </section>

          {/* Footer */}
          <footer className="text-center text-[#b0b0b0] text-sm pt-8 border-t border-[#2a2a2a]">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="opus-gradient-text font-semibold">Opus Hub</span>
              <span>•</span>
              <span>Inteligência Artificial & Automação</span>
            </div>
            <p>Relatório gerado automaticamente | Belevita ROI Dashboard</p>
            <p className="mt-1">Período: Julho - Dezembro 2025</p>
          </footer>
        </div>
      </main>
    </TooltipProvider>
  )
}
