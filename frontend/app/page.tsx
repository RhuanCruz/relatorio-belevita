"use client"

import Image from "next/image"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Bar, BarChart, XAxis, YAxis, Pie, PieChart, Cell, Label } from "recharts"
import { MessageSquare, Bot, DollarSign, ShieldCheck, AlertTriangle, Clock, TrendingUp, Package, HelpCircle, Users, CheckCircle, Target, Zap } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { metricsData } from "@/lib/data"
import { motion } from "framer-motion"
import { useRef } from "react"

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

// Animation variants
const fadeInUp = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: "easeOut" as const }
  }
}

const fadeIn = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.6, ease: "easeOut" as const }
  }
}

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.2
    }
  }
}

const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.5, ease: "easeOut" as const }
  }
}

// Componente de Seção com Snap
function Section({ id, children, className = "" }: { id: string; children: React.ReactNode; className?: string }) {
  return (
    <section
      id={id}
      className={`h-screen snap-start snap-always flex flex-col justify-center overflow-hidden ${className}`}
    >
      {children}
    </section>
  )
}

// Componente de Título de Seção Animado
function SectionHeader({ number, title, subtitle }: { number: string; title: string; subtitle?: string }) {
  return (
    <motion.div
      className="mb-12"
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.5 }}
    >
      <div className="flex items-center gap-4 mb-2">
        <span className="text-sm font-mono text-[#00f2fe] opacity-60">{number}</span>
        <div className="h-px flex-1 bg-gradient-to-r from-[#00f2fe]/30 to-transparent" />
      </div>
      <h2 className="text-3xl font-bold text-[#f0f0f0]">{title}</h2>
      {subtitle && <p className="text-[#b0b0b0] mt-2 text-lg">{subtitle}</p>}
    </motion.div>
  )
}

// Componente de Métrica Hero Animado
function HeroMetric({ icon: Icon, label, value, subtext, color = "#00f2fe", delay = 0 }: {
  icon: any;
  label: string;
  value: string;
  subtext: string;
  color?: string;
  delay?: number;
}) {
  return (
    <motion.div
      className="text-center p-8"
      variants={scaleIn}
    >
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4" style={{ background: `${color}20` }}>
        <Icon className="h-8 w-8" style={{ color }} />
      </div>
      <p className="text-[#b0b0b0] text-sm uppercase tracking-wider mb-2">{label}</p>
      <p className="text-5xl font-bold mb-2" style={{ color }}>{value}</p>
      <p className="text-[#b0b0b0] text-sm">{subtext}</p>
    </motion.div>
  )
}

export default function Dashboard() {
  return (
    <TooltipProvider>
      {/* Container com Snap Scroll */}
      <main className="h-screen overflow-y-scroll snap-y snap-mandatory bg-[#0a0a0a] scroll-smooth">

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 1: CAPA
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="capa" className="relative overflow-hidden">
          {/* Background Gradient */}
          <div className="absolute inset-0 opacity-30">
            <motion.div
              className="absolute top-0 left-0 w-96 h-96 bg-[#00f2fe] rounded-full filter blur-[150px]"
              animate={{
                x: [0, 50, 0],
                y: [0, 30, 0],
              }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div
              className="absolute bottom-0 right-0 w-96 h-96 bg-[#6a11cb] rounded-full filter blur-[150px]"
              animate={{
                x: [0, -50, 0],
                y: [0, -30, 0],
              }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            />
          </div>

          <div className="container mx-auto max-w-5xl px-8 relative z-10">
            {/* Logos */}
            <motion.div
              className="flex items-center justify-between mb-24"
              initial={{ opacity: 0, y: -30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <Image
                src="/opus-logo.png"
                alt="Opus Hub"
                width={160}
                height={50}
                className="opacity-90"
              />
              <div className="text-right">
                <p className="text-[#b0b0b0] text-sm">Preparado para</p>
                <p className="text-[#f0f0f0] text-xl font-semibold">Belevita</p>
              </div>
            </motion.div>

            {/* Título Principal */}
            <motion.div
              className="text-center mb-16"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
            >
              <p className="text-[#00f2fe] text-sm uppercase tracking-[0.3em] mb-4">Relatório de Performance</p>
              <h1 className="text-5xl md:text-6xl font-bold text-[#f0f0f0] mb-6">
                Agente de IA
                <br />
                <span className="opus-gradient-text">Resultados 2025</span>
              </h1>
              <p className="text-[#b0b0b0] text-xl">Análise completa do atendimento automatizado</p>
            </motion.div>

            {/* Período */}
            <motion.div
              className="flex justify-center"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.6 }}
            >
              <div className="inline-flex items-center gap-4 bg-[#151515] px-8 py-4 rounded-full border border-[#2a2a2a]">
                <Clock className="h-5 w-5 text-[#4facfe]" />
                <span className="text-[#f0f0f0]">Período: Julho - Dezembro 2025</span>
              </div>
            </motion.div>

            {/* Scroll Indicator */}
            <motion.div
              className="absolute bottom-8 left-1/2 -translate-x-1/2"
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <div className="w-6 h-10 border-2 border-[#4facfe]/50 rounded-full flex justify-center pt-2">
                <motion.div
                  className="w-1.5 h-3 bg-[#4facfe] rounded-full"
                  animate={{ y: [0, 12, 0], opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
              </div>
            </motion.div>
          </div>
        </Section>

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 2: SUMÁRIO EXECUTIVO
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="sumario">
          <div className="container mx-auto max-w-5xl px-8">
            <SectionHeader
              number="01"
              title="Sumário Executivo"
              subtitle="Os números que importam"
            />

            {/* Hero Metrics Grid */}
            <motion.div
              className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.3 }}
            >
              <motion.div variants={scaleIn} className="bg-[#151515] rounded-2xl border border-[#2a2a2a] overflow-hidden">
                <HeroMetric
                  icon={DollarSign}
                  label="Economia Gerada"
                  value={`R$ ${(metricsData.financeiro.economiaReais / 1000).toFixed(0)}K`}
                  subtext={`${metricsData.financeiro.horasEconomizadas.toLocaleString()} horas poupadas`}
                  color="#00f2fe"
                />
              </motion.div>

              <motion.div variants={scaleIn} className="bg-[#151515] rounded-2xl border border-[#2a2a2a] overflow-hidden">
                <HeroMetric
                  icon={Bot}
                  label="Resolução IA"
                  value={`${metricsData.kpis.taxaResolucaoIA}%`}
                  subtext="Sem escalação humana"
                  color="#4facfe"
                />
              </motion.div>

              <motion.div variants={scaleIn} className="bg-[#151515] rounded-2xl border border-[#2a2a2a] overflow-hidden">
                <HeroMetric
                  icon={ShieldCheck}
                  label="Revenue Protegido"
                  value={`R$ ${(metricsData.financeiro.revenueAtRisk / 1000).toFixed(0)}K`}
                  subtext={`${metricsData.financeiro.conversasCriticas.toLocaleString()} conversas críticas`}
                  color="#6a11cb"
                />
              </motion.div>
            </motion.div>

            {/* Contexto */}
            <motion.div
              className="bg-[#151515]/50 rounded-xl p-8 border border-[#2a2a2a]"
              variants={fadeInUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.5 }}
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                <div>
                  <p className="text-3xl font-bold text-[#f0f0f0]">{metricsData.kpis.totalConversas.toLocaleString()}</p>
                  <p className="text-[#b0b0b0] text-sm">Conversas Analisadas</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[#f0f0f0]">{metricsData.kpis.totalPedidos.toLocaleString()}</p>
                  <p className="text-[#b0b0b0] text-sm">Pedidos no Período</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[#f0f0f0]">{metricsData.kpis.taxaContato}%</p>
                  <p className="text-[#b0b0b0] text-sm">Taxa de Contato</p>
                </div>
                <div>
                  <p className="text-3xl font-bold text-[#f0f0f0]">R$ {metricsData.kpis.ticketMedio}</p>
                  <p className="text-[#b0b0b0] text-sm">Ticket Médio</p>
                </div>
              </div>
            </motion.div>
          </div>
        </Section>

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 3: PERFORMANCE DA IA
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="performance">
          <div className="container mx-auto max-w-5xl px-8">
            <SectionHeader
              number="02"
              title="Performance da IA"
              subtitle="Como o agente está resolvendo problemas"
            />

            <motion.div
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
            >
              {/* Left: KPIs */}
              <motion.div className="space-y-4" variants={fadeInUp}>
                <Card className="bg-[#151515] border-[#2a2a2a]">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-[#b0b0b0] text-sm">Taxa de Resolução Autônoma</p>
                        <p className="text-4xl font-bold text-[#00f2fe] mt-1">{metricsData.kpis.taxaResolucaoIA}%</p>
                      </div>
                      <div className="w-20 h-20 rounded-full border-4 border-[#00f2fe] flex items-center justify-center">
                        <CheckCircle className="h-10 w-10 text-[#00f2fe]" />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-[#151515] border-[#2a2a2a]">
                  <CardContent className="p-6">
                    <p className="text-[#b0b0b0] text-sm mb-4">Chamados WISMO (Onde está meu pedido?)</p>
                    <div className="flex items-end gap-4">
                      <p className="text-4xl font-bold text-[#4facfe]">{metricsData.wismo}%</p>
                      <p className="text-[#b0b0b0] text-sm pb-1">de todos os atendimentos</p>
                    </div>
                    <div className="mt-4 h-2 bg-[#2a2a2a] rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: 'linear-gradient(90deg, #00f2fe, #4facfe)' }}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${metricsData.wismo}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, delay: 0.5 }}
                      />
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-[#151515] border-[#2a2a2a]">
                  <CardContent className="p-6">
                    <p className="text-[#b0b0b0] text-sm mb-4">Sentimento das Conversas</p>
                    <div className="flex gap-4">
                      {metricsData.sentimento.map((item, index) => (
                        <div key={item.tipo} className="flex-1 text-center">
                          <p className="text-2xl font-bold" style={{ color: COLORS[index] }}>
                            {Math.round((item.quantidade / metricsData.kpis.totalConversas) * 100)}%
                          </p>
                          <p className="text-[#b0b0b0] text-xs">{item.tipo}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Right: Chart */}
              <motion.div variants={fadeInUp}>
                <Card className="bg-[#151515] border-[#2a2a2a] h-full">
                  <CardHeader>
                    <CardTitle className="text-[#f0f0f0]">Motivos de Contato</CardTitle>
                    <CardDescription className="text-[#b0b0b0]">Principais intenções dos clientes</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ChartContainer config={chartConfig} className="h-[280px] w-full">
                      <BarChart data={metricsData.intencoes} layout="vertical" accessibilityLayer>
                        <XAxis type="number" stroke="#b0b0b0" />
                        <YAxis dataKey="name" type="category" width={120} stroke="#b0b0b0" />
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
              </motion.div>
            </motion.div>
          </div>
        </Section>

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 4: INSIGHTS OPERACIONAIS
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="insights">
          <div className="container mx-auto max-w-5xl px-8">
            <SectionHeader
              number="03"
              title="Insights Operacionais"
              subtitle="Onde estão os gargalos"
            />

            <motion.div
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
            >
              {/* Produtos com Problemas */}
              <motion.div variants={fadeInUp}>
                <Card className="bg-[#151515] border-[#2a2a2a]">
                  <CardHeader>
                    <CardTitle className="text-[#f0f0f0]">Produtos com Mais Reclamações</CardTitle>
                    <CardDescription className="text-[#b0b0b0]">Categorias que geram mais atrito</CardDescription>
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
              </motion.div>

              {/* Atendimentos por Hora */}
              <motion.div variants={fadeInUp}>
                <Card className="bg-[#151515] border-[#2a2a2a]">
                  <CardHeader>
                    <CardTitle className="text-[#f0f0f0]">Distribuição por Horário</CardTitle>
                    <CardDescription className="text-[#b0b0b0]">Quando os clientes mais procuram</CardDescription>
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
              </motion.div>
            </motion.div>
          </div>
        </Section>

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 5: RISCOS E ALERTAS
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="riscos">
          <div className="container mx-auto max-w-5xl px-8">
            <SectionHeader
              number="04"
              title="Riscos & Alertas"
              subtitle="Pontos de atenção identificados"
            />

            <motion.div
              className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8"
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
            >
              {/* Alertas de Risco Total */}
              <motion.div variants={scaleIn}>
                <Card className="bg-[#151515] border-[#ef4444]/30 h-full">
                  <CardContent className="p-6 text-center">
                    <AlertTriangle className="h-12 w-12 text-[#ef4444] mx-auto mb-4" />
                    <p className="text-5xl font-bold text-[#ef4444]">
                      {metricsData.risco.reduce((a, b) => a + b.quantidade, 0)}
                    </p>
                    <p className="text-[#b0b0b0] mt-2">Menções Críticas</p>
                    <p className="text-[#666] text-sm mt-4">PROCON, Reclame Aqui, Golpe, Estorno</p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Vazamento de Tool */}
              <motion.div variants={scaleIn}>
                <Card className="bg-[#151515] border-[#ef4444]/30 h-full">
                  <CardContent className="p-6 text-center">
                    <Zap className="h-12 w-12 text-[#ef4444] mx-auto mb-4" />
                    <p className="text-5xl font-bold text-[#ef4444]">
                      {((metricsData.errosIA?.toolLeaks || 0) / metricsData.kpis.totalConversas * 100).toFixed(2)}%
                    </p>
                    <p className="text-[#b0b0b0] mt-2">Vazamento de Tool</p>
                    <p className="text-[#666] text-sm mt-4">{metricsData.errosIA?.toolLeaks || 0} conversas afetadas</p>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Cliente Percebeu IA */}
              <motion.div variants={scaleIn}>
                <Card className="bg-[#151515] border-[#f97316]/30 h-full">
                  <CardContent className="p-6 text-center">
                    <Bot className="h-12 w-12 text-[#f97316] mx-auto mb-4" />
                    <p className="text-5xl font-bold text-[#f97316]">
                      {((metricsData.errosIA?.percebeuIA || 0) / metricsData.kpis.totalConversas * 100).toFixed(1)}%
                    </p>
                    <p className="text-[#b0b0b0] mt-2">Perceberam ser IA</p>
                    <p className="text-[#666] text-sm mt-4">{metricsData.errosIA?.percebeuIA || 0} clientes notaram</p>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>

            {/* Termômetro de Risco */}
            <motion.div
              variants={fadeInUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.3 }}
            >
              <Card className="bg-[#151515] border-[#2a2a2a]">
                <CardHeader>
                  <CardTitle className="text-[#f0f0f0]">Detalhamento de Riscos</CardTitle>
                </CardHeader>
                <CardContent>
                  <ChartContainer config={chartConfig} className="h-[180px] w-full">
                    <BarChart data={metricsData.risco} layout="vertical" accessibilityLayer>
                      <XAxis type="number" stroke="#b0b0b0" />
                      <YAxis dataKey="tipo" type="category" width={120} stroke="#b0b0b0" />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="quantidade" fill="#ef4444" radius={4} />
                    </BarChart>
                  </ChartContainer>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </Section>

        {/* ═══════════════════════════════════════════════════════════════════
            SEÇÃO 6: RECOMENDAÇÕES
        ═══════════════════════════════════════════════════════════════════ */}
        <Section id="recomendacoes">
          <div className="container mx-auto max-w-5xl px-8">
            <SectionHeader
              number="05"
              title="Recomendações"
              subtitle="Ações prioritárias para os próximos meses"
            />

            <motion.div
              className="space-y-6"
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.2 }}
            >
              {/* Recomendação 1 */}
              <motion.div
                className="bg-[#151515] rounded-xl p-6 border-l-4 border-[#00f2fe]"
                variants={fadeInUp}
              >
                <div className="flex items-start gap-4">
                  <div className="bg-[#00f2fe]/10 p-3 rounded-lg">
                    <Target className="h-6 w-6 text-[#00f2fe]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-[#f0f0f0] mb-2">Automatizar Alertas de Rastreio</h3>
                    <p className="text-[#b0b0b0]">
                      40.7% dos chamados são WISMO. Implementar notificações proativas de status de pedido pode reduzir esse volume em até 60%.
                    </p>
                    <div className="mt-4 flex items-center gap-2 text-[#00f2fe] text-sm">
                      <span className="bg-[#00f2fe]/10 px-3 py-1 rounded-full">Alto Impacto</span>
                      <span className="bg-[#00f2fe]/10 px-3 py-1 rounded-full">Médio Esforço</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Recomendação 2 */}
              <motion.div
                className="bg-[#151515] rounded-xl p-6 border-l-4 border-[#4facfe]"
                variants={fadeInUp}
              >
                <div className="flex items-start gap-4">
                  <div className="bg-[#4facfe]/10 p-3 rounded-lg">
                    <Package className="h-6 w-6 text-[#4facfe]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-[#f0f0f0] mb-2">Revisar Categoria Calçados</h3>
                    <p className="text-[#b0b0b0]">
                      Calçados lidera em reclamações. Sugerimos: melhorar tabela de medidas, revisar qualidade do fornecedor, e criar FAQ específico.
                    </p>
                    <div className="mt-4 flex items-center gap-2 text-[#4facfe] text-sm">
                      <span className="bg-[#4facfe]/10 px-3 py-1 rounded-full">Alto Impacto</span>
                      <span className="bg-[#4facfe]/10 px-3 py-1 rounded-full">Alto Esforço</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Recomendação 3 */}
              <motion.div
                className="bg-[#151515] rounded-xl p-6 border-l-4 border-[#6a11cb]"
                variants={fadeInUp}
              >
                <div className="flex items-start gap-4">
                  <div className="bg-[#6a11cb]/10 p-3 rounded-lg">
                    <Bot className="h-6 w-6 text-[#6a11cb]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-[#f0f0f0] mb-2">Corrigir Vazamentos de Tool</h3>
                    <p className="text-[#b0b0b0]">
                      {metricsData.errosIA?.toolLeaks || 0} conversas expuseram código interno. Ajustar prompts e adicionar sanitização de outputs.
                    </p>
                    <div className="mt-4 flex items-center gap-2 text-[#6a11cb] text-sm">
                      <span className="bg-[#6a11cb]/10 px-3 py-1 rounded-full">Médio Impacto</span>
                      <span className="bg-[#6a11cb]/10 px-3 py-1 rounded-full">Baixo Esforço</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </Section>

      </main>
    </TooltipProvider>
  )
}
