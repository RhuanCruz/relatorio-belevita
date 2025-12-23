// Dados das métricas extraídas do Supabase
// Gerado automaticamente por scripts/metrics_extractor.py

import metricsJson from "./metrics.json";

export const metricsData = {
    kpis: metricsJson.kpis,
    financeiro: metricsJson.financeiro,
    sentimento: metricsJson.sentimento,
    intencoes: metricsJson.intencoes.map((i: { name: string; value: number }) => ({
        name: i.name.replace("DÃºvida", "Dúvida"),
        value: i.value,
    })),
    produtosProblemas: metricsJson.produtosProblemas.map((p: { categoria: string; reclamacoes: number }) => ({
        categoria: p.categoria
            .replace("CalÃ§ados", "Calçados")
            .replace("CalÃ§as", "Calças")
            .replace("AcessÃ³rios", "Acessórios")
            .replace("Moda Ãntima", "Moda Íntima"),
        reclamacoes: p.reclamacoes,
    })),
    risco: metricsJson.risco,
    volumeMensal: metricsJson.volumeMensal.map((v: { mes: string; atendimentos: number }) => ({
        mes: v.mes,
        atendimentos: v.atendimentos,
    })),
    porHora: metricsJson.porHora,
    errosIA: metricsJson.errosIA,
    wismo: metricsJson.wismo,
    geradoEm: metricsJson.geradoEm,
};
