"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Area, AreaChart, CartesianGrid, Cell, Label } from "recharts"
import { MessageSquare, Bot, DollarSign, ShieldCheck, AlertTriangle, Clock, TrendingUp, Package, HelpCircle, Users } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Separator } from "@/components/ui/separator"
import { metricsData } from "@/lib/data"

const COLORS = ["#3b82f6", "#1d8ecf", "#0eb1e2", "#0f13e4", "#5ca4f6"]

const chartConfig = {
  atendimentos: { label: "Atendimentos", color: "#3b82f6" },
  quantidade: { label: "Quantidade", color: "#1d8ecf" },
  reclamacoes: { label: "Reclamações", color: "#0f13e4" },
  value: { label: "Quantidade", color: "#0eb1e2" },
} satisfies ChartConfig

const sentimentoConfig = {
  quantidade: { label: "Quantidade" },
  Positivo: { label: "Positivo", color: "#3b82f6" },
  Neutro: { label: "Neutro", color: "#1d8ecf" },
  Negativo: { label: "Negativo", color: "#0f13e4" },
} satisfies ChartConfig

// Componente de ajuda reutilizável
function HelpTooltip({ text }: { text: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <HelpCircle className="h-4 w-4 text-zinc-400 cursor-help" />
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-xs text-sm">
        <p>{text}</p>
      </TooltipContent>
    </Tooltip>
  )
}

export default function Dashboard() {
  return (
    <TooltipProvider>
      <main className="min-h-screen bg-zinc-50">
        <div className="container mx-auto max-w-6xl px-8 py-16">
          {/* Header */}
          <header className="mb-12">
            <h1 className="text-3xl font-semibold text-zinc-900">Relatório Belevita - 2025</h1>
            <p className="text-zinc-500 mt-1">Análise de performance do agente IA</p>
          </header>

          {/* KPI Cards - Linha 1 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Taxa de Contato</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Percentual de pedidos que geraram um chamado no suporte. Calculado como: (Total de Conversas ÷ Total de Pedidos) × 100. Meta ideal: abaixo de 30%." />
                  <MessageSquare className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metricsData.kpis.taxaContato}%</div>
                <p className="text-xs text-zinc-500">{metricsData.kpis.totalConversas.toLocaleString()} chamados / {metricsData.kpis.totalPedidos.toLocaleString()} pedidos</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Resolução IA</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Percentual de conversas resolvidas 100% pela IA, sem necessidade de transbordo para atendente humano." />
                  <Bot className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{metricsData.kpis.taxaResolucaoIA}%</div>
                <p className="text-xs text-zinc-500">sem escalação humana</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Economia Gerada</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text={`Valor economizado com atendimento automatizado. Calculado como: Horas Economizadas × Custo/Hora (R$ ${metricsData.kpis.custoHoraAtendente}). Estimativa de 10 minutos por conversa.`} />
                  <DollarSign className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">R$ {metricsData.financeiro.economiaReais.toLocaleString()}</div>
                <p className="text-xs text-zinc-500">{metricsData.financeiro.horasEconomizadas.toLocaleString()} horas poupadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Revenue Protegido</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text={`Valor em pedidos que a IA ajudou a reter, evitando cancelamentos. Calculado como: Conversas Críticas × Ticket Médio (R$ ${metricsData.kpis.ticketMedio}).`} />
                  <ShieldCheck className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">R$ {(metricsData.financeiro.revenueAtRisk / 1000).toFixed(0)}K</div>
                <p className="text-xs text-zinc-500">{metricsData.financeiro.conversasCriticas.toLocaleString()} conversas críticas</p>
              </CardContent>
            </Card>
          </section>

          {/* KPI Cards - Linha 2 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Conversas</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Número total de sessões de chat únicas registradas no período analisado." />
                  <Users className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metricsData.kpis.totalConversas.toLocaleString()}</div>
                <p className="text-xs text-zinc-500">no período analisado</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Ticket Médio</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Valor médio de cada pedido na loja. Usado para calcular Revenue at Risk e outras métricas financeiras." />
                  <Package className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">R$ {metricsData.kpis.ticketMedio}</div>
                <p className="text-xs text-zinc-500">valor médio por pedido</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">WISMO</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="'Where Is My Order' - Percentual de chamados sobre rastreamento de pedido. Detectado por palavras-chave como 'onde está', 'rastreio', 'quando chega'." />
                  <Clock className="h-4 w-4 text-zinc-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metricsData.wismo}%</div>
                <p className="text-xs text-zinc-500">chamados sobre rastreio</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Alertas de Risco</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Menções críticas que indicam risco de perda de cliente. Inclui: PROCON, Reclame Aqui, acusações de golpe e pedidos de estorno/chargeback." />
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{metricsData.risco.reduce((a, b) => a + b.quantidade, 0)}</div>
                <p className="text-xs text-zinc-500">menções críticas detectadas</p>
              </CardContent>
            </Card>
          </section>

          {/* Erros de IA - Seção Crítica */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
            <Card className="border-red-200">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Vazamento de Tool</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Mensagens onde a IA mostrou código interno, como <tool_code>, print(default_api...), ou instruções internas. Isso revela que é uma IA e não um humano." />
                  <AlertTriangle className="h-4 w-4 text-red-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {((metricsData.errosIA?.toolLeaks || 0) / metricsData.kpis.totalConversas * 100).toFixed(2)}%
                </div>
                <p className="text-xs text-zinc-500">
                  {metricsData.errosIA?.toolLeaks || 0} conversas com vazamento
                </p>
              </CardContent>
            </Card>

            <Card className="border-orange-200">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Cliente Percebeu IA</CardTitle>
                <div className="flex items-center gap-2">
                  <HelpTooltip text="Conversas onde o cliente mencionou que percebeu ser uma IA, usando termos como 'robô', 'bot', 'automático', 'quero falar com humano'." />
                  <Bot className="h-4 w-4 text-orange-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {((metricsData.errosIA?.percebeuIA || 0) / metricsData.kpis.totalConversas * 100).toFixed(1)}%
                </div>
                <p className="text-xs text-zinc-500">
                  {metricsData.errosIA?.percebeuIA || 0} clientes notaram
                </p>
              </CardContent>
            </Card>
          </section>

          <Separator className="mb-12" />

          {/* Volume Chart */}


          {/* Grid Charts - Linha 1 */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {/* Intenções */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Motivos de Contato</CardTitle>
                  <HelpTooltip text="Classificação automática das intenções dos clientes. Detectado por palavras-chave: Rastreio (onde está, rastrear), Troca (trocar, devolver), Cancelamento (cancelar), Dúvida (como funciona)." />
                </div>
                <CardDescription>Distribuição por intenção</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.intencoes} layout="vertical" accessibilityLayer>
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={100} />
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
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Produtos com Problemas</CardTitle>
                  <HelpTooltip text="Categorias de produtos mais mencionadas em conversas com indicadores de problema (reclamação, defeito, troca). Quanto maior a barra, maior a dor de cabeça operacional." />
                </div>
                <CardDescription>Categorias mais reclamadas</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.produtosProblemas} accessibilityLayer>
                    <XAxis dataKey="categoria" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="reclamacoes" fill="#0f13e4" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Sentimento */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Sentimento</CardTitle>
                  <HelpTooltip text="Análise de sentimento das conversas baseada em palavras-chave. Positivo (obrigado, ótimo), Neutro (ok, entendi), Negativo (frustrado, absurdo)." />
                </div>
                <CardDescription>Distribuição geral</CardDescription>
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
                      <Label value={`${Math.round((metricsData.sentimento[0].quantidade / metricsData.kpis.totalConversas) * 100)}%`} position="center" className="text-2xl font-bold" />
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
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Atendimentos por Hora</CardTitle>
                  <HelpTooltip text="Distribuição de atendimentos ao longo do dia. Útil para identificar horários de pico e calcular economia com atendimento noturno (19h-08h)." />
                </div>
                <CardDescription>Distribuição ao longo do dia</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.porHora} accessibilityLayer>
                    <XAxis dataKey="hora" />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="quantidade" fill="#5ca4f6" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Termômetro de Risco */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Termômetro de Risco</CardTitle>
                  <HelpTooltip text="Menções críticas que indicam risco legal ou financeiro. PROCON/Reclame Aqui = risco de reputação. Estorno = risco de chargeback. Acompanhe tendências mensais." />
                </div>
                <CardDescription>Menções críticas detectadas</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[280px] w-full">
                  <BarChart data={metricsData.risco} layout="vertical" accessibilityLayer>
                    <XAxis type="number" />
                    <YAxis dataKey="tipo" type="category" width={100} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar dataKey="quantidade" fill="#0f13e4" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </section>

          <Separator className="mb-12" />

          {/* Seção de Resumo */}
          <section className="mb-12">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-xl font-semibold text-zinc-800">Resumo Executivo</h2>
              <HelpTooltip text="Síntese dos principais insights do período. Ganhos = resultados positivos. Alertas = pontos que requerem atenção. Oportunidades = ações sugeridas." />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="border-green-200 bg-green-50">
                <CardHeader>
                  <CardTitle className="text-green-700 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Ganhos
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-green-800">• Economia de R$ {metricsData.financeiro.economiaReais.toLocaleString()} em atendimento</p>
                  <p className="text-sm text-green-800">• {metricsData.kpis.taxaResolucaoIA}% resolvido pela IA</p>
                  <p className="text-sm text-green-800">• R$ {(metricsData.financeiro.revenueAtRisk / 1000).toFixed(0)}K em pedidos protegidos</p>
                </CardContent>
              </Card>

              <Card className="border-red-200 bg-red-50">
                <CardHeader>
                  <CardTitle className="text-red-700 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Alertas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-red-800">• Taxa de contato alta: {metricsData.kpis.taxaContato}%</p>
                  <p className="text-sm text-red-800">• {metricsData.produtosProblemas[0].reclamacoes} reclamações em Calçados</p>
                  <p className="text-sm text-red-800">• {metricsData.risco.reduce((a, b) => a + b.quantidade, 0)} menções de risco</p>
                </CardContent>
              </Card>

              <Card className="border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="text-blue-700 flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    Oportunidades
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-blue-800">• 40.7% dos chamados são WISMO - automatizar alertas</p>
                  <p className="text-sm text-blue-800">• Revisar fornecedor de Calçados</p>
                  <p className="text-sm text-blue-800">• Melhorar tabela de medidas</p>
                </CardContent>
              </Card>
            </div>
          </section>

          {/* Footer */}
          <footer className="text-center text-zinc-400 text-sm pt-8 border-t">
            <p>Gerado automaticamente | Belevita ROI Dashboard</p>
            <p className="mt-1">Período: Julho - Dezembro 2025</p>
          </footer>
        </div>
      </main>
    </TooltipProvider>
  )
}
