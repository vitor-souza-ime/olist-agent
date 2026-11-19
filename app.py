from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import gradio as gr
import pandas as pd

from olist_agent.data import enrich_reviews, load_zip_dataset
from olist_agent.engine import analyze_batch, analyze_review, build_executive_summary, THEME_LABELS
from olist_agent.llm import analyze_with_openrouter

ROOT = Path(__file__).parent
DEMO_PATH = ROOT / "data" / "demo_reviews.csv"
DEMO_DF = pd.read_csv(DEMO_PATH)


def load_user_files(files):
    if not files:
        return DEMO_DF.copy(), "Casos sintéticos de demonstração (10 registros)."
    if not isinstance(files, list):
        files = [files]
    tables = {}
    for item in files:
        path = item if isinstance(item, str) else getattr(item, "name", None)
        if not path:
            continue
        name = Path(path).name.lower()
        if name.endswith(".zip"):
            tables.update(load_zip_dataset(Path(path).read_bytes()))
        elif name.endswith(".csv") or name.endswith(".csv.gz"):
            df = pd.read_csv(path, compression="gzip" if name.endswith(".gz") else "infer", low_memory=False)
            key = name.replace(".csv.gz", "").replace(".csv", "")
            tables[key] = df
    reviews = next((v.copy() for k, v in tables.items() if "review" in k or "review_score" in v.columns), None)
    if reviews is None:
        raise ValueError("Não foi encontrada a tabela de avaliações. Envie olist_order_reviews_dataset.csv ou um ZIP do dataset.")
    orders = next((v for k, v in tables.items() if "orders_dataset" in k or k.endswith("orders")), None)
    items = next((v for k, v in tables.items() if "order_items" in k), None)
    products = next((v for k, v in tables.items() if "products_dataset" in k or k == "products"), None)
    sellers = next((v for k, v in tables.items() if "sellers_dataset" in k or k == "sellers"), None)
    reviews = enrich_reviews(reviews, orders=orders, items=items, products=products, sellers=sellers)
    return reviews, f"Arquivos do usuário ({len(reviews):,} avaliações)."


def summary_markdown(results: pd.DataFrame, source_label: str) -> str:
    s = build_executive_summary(results)
    if not s["total"]:
        return "Nenhuma avaliação disponível."
    top = "\n".join(
        f"{i}. **{x['label']}** — {x['count']} ({x['share_pct']}%); área: {x['area']}.\n   Ação: {x['recommendation']}"
        for i, x in enumerate(s["top_causes"], 1)
    )
    return (
        f"### Resumo executivo\n\n"
        f"Fonte: {source_label}\n\n"
        f"- Avaliações processadas: **{s['total']}**\n"
        f"- Nota média: **{s['average_score'] if s['average_score'] is not None else 'não disponível'}**\n"
        f"- Comentários negativos: **{s['negative']}**\n"
        f"- Casos críticos: **{s['critical']}**\n"
        f"- Revisão humana obrigatória: **{s['human_review']}**\n"
        f"- Sem comentário textual: **{s['no_comment']}**\n\n"
        f"### Causas mais frequentes (classificação primária)\n\n{top}\n\n"
        f"> Frequências referem-se somente ao arquivo carregado. Não representam estimativas de toda a operação Olist."
    )


def analyze_single(score, title, comment, api_key, model):
    result = analyze_review({"review_score": score, "review_comment_title": title, "review_comment_message": comment})
    lines = [
        "### Resultado do agente",
        f"- Sentimento: **{result['sentiment']}**",
        f"- Tema: **{result['theme_label']}**",
        f"- Severidade: **{result['severity']}**",
        f"- Área responsável sugerida: **{result['responsible_area']}**",
        f"- Revisão humana: **{'Obrigatória' if result['needs_human_review'] else ('Recomendada' if result['human_review_reason'] else 'Não indicada')}**",
        f"- Divergência nota/texto: **{'Sim' if result['score_text_discrepancy'] else 'Não'}**",
        "",
        "**Evidência analisada**",
        f"> {result['evidence']}",
        "",
        "**Recomendação**",
        result["recommendation"],
    ]
    if result["human_review_reason"]:
        lines += ["", f"**Encaminhamento:** {result['human_review_reason']}"]
    lines += ["", "*Classificação local baseada em regras explícitas; não é probabilidade calibrada nem decisão final sobre responsabilidade.*"]
    llm_output = "A integração OpenRouter está desabilitada. Informe uma chave para solicitar uma segunda análise generativa."
    if api_key:
        try:
            llm_output = json.dumps(analyze_with_openrouter({"score": score, "title": title, "comment": comment}, api_key, model), ensure_ascii=False, indent=2)
        except Exception as exc:
            llm_output = f"Falha na chamada ao OpenRouter: {exc}"
    return "\n".join(lines), result, llm_output


def analyze_uploaded(files, max_rows):
    try:
        df, source_label = load_user_files(files)
        if max_rows and int(max_rows) > 0:
            df = df.head(int(max_rows))
        results = analyze_batch(df)
        summary = summary_markdown(results, source_label)
        path = Path(tempfile.gettempdir()) / "olist_reviews_analysis.csv"
        results.to_csv(path, index=False, encoding="utf-8-sig")
        return summary, results, str(path), source_label
    except Exception as exc:
        return f"**Erro ao carregar/processar os dados:** {exc}", pd.DataFrame(), None, "Erro"


def overview(files):
    try:
        df, label = load_user_files(files)
        results = analyze_batch(df)
        table = results[["review_id", "review_score", "sentiment", "theme_label", "severity", "needs_human_review"]].copy()
        return summary_markdown(results, label), table
    except Exception as exc:
        return f"Erro: {exc}", pd.DataFrame()


def run_validation():
    cases = [
        ("T1 — Pedido incompleto", 1, "Comprei oito fronhas, mas chegaram apenas quatro.", "incomplete_order", "Alta", False, False),
        ("T2 — Nota e texto divergentes", 5, "Meu produto era para ter chegado até 15/08, mas até hoje não recebi.", "delivery", "Alta", False, True),
        ("T3 — Alegação crítica", 1, "O cartucho chegou embolorado e parece falsificado.", "critical_integrity_safety", "Crítica", True, False),
        ("T4 — Experiência positiva", 5, "Chegou antes do prazo e o produto corresponde ao anunciado.", "positive_experience", "Baixa", False, False),
        ("T5 — Comentário ausente", 3, "", "no_comment", "Indeterminada", False, False),
    ]
    rows = []
    for name, score, comment, expected_theme, expected_severity, expected_flag, expected_discrepancy in cases:
        actual = analyze_review({"review_score": score, "review_comment_message": comment})
        passed = (actual["theme"] == expected_theme and actual["severity"] == expected_severity
                  and actual["needs_human_review"] == expected_flag
                  and actual["score_text_discrepancy"] == expected_discrepancy)
        rows.append({
            "Teste": name,
            "Tema esperado": THEME_LABELS[expected_theme],
            "Tema obtido": actual["theme_label"],
            "Severidade": actual["severity"],
            "Revisão humana": "Obrigatória" if actual["needs_human_review"] else ("Recomendada" if actual["human_review_reason"] else "Não indicada"),
            "Divergência nota/texto": actual["score_text_discrepancy"],
            "Resultado": "APROVADO" if passed else "REPROVADO",
        })
    frame = pd.DataFrame(rows)
    passed = int((frame["Resultado"] == "APROVADO").sum())
    status = f"### Resultado da validação: {passed}/5 cenários aprovados\n\n"
    status += "Todos os cenários funcionais previstos passaram." if passed == 5 else "Há cenários que precisam de ajuste."
    status += "\n\nOs cinco registros são casos sintéticos controlados, não extraídos do dataset Olist."
    return status, frame


def launch():
    with gr.Blocks(title="Olist Intelligent Reviews") as demo:
        gr.Markdown("# ⭐ Olist Intelligent Reviews\nTransformando avaliações de clientes em sinais operacionais, prioridades e ações recomendadas.\n\n**Protótipo acadêmico — Tech Challenge Fase 3.** Não é um sistema oficial da Olist.")
        with gr.Row():
            files = gr.File(label="CSV(s) ou ZIP do dataset Olist (opcional)", file_count="multiple", file_types=[".csv", ".zip", ".gz"], type="filepath")
            gr.Markdown("**Sem upload:** a aplicação utiliza 10 casos sintéticos de demonstração. Para análise de negócio, carregue olist_order_reviews_dataset.csv ou o ZIP do dataset. Para enriquecer, envie também orders, order_items, products e sellers.")
        with gr.Tab("Visão geral"):
            overview_btn = gr.Button("Atualizar visão executiva", variant="primary")
            overview_md = gr.Markdown()
            overview_table = gr.Dataframe(label="Avaliações classificadas", interactive=False)
            overview_btn.click(overview, inputs=[files], outputs=[overview_md, overview_table])
        with gr.Tab("Analisar avaliação"):
            gr.Markdown("Insira uma avaliação ou utilize os casos da aba de validação.")
            with gr.Row():
                score = gr.Slider(1, 5, value=3, step=1, label="Nota da avaliação")
                title = gr.Textbox(label="Título (opcional)")
            comment = gr.Textbox(label="Comentário do cliente", lines=4, placeholder="Cole o comentário...")
            with gr.Accordion("Integração generativa opcional (OpenRouter)", open=False):
                api_key = gr.Textbox(label="OpenRouter API key", type="password", value=os.getenv("OPENROUTER_API_KEY", ""))
                model = gr.Textbox(label="Modelo", value=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b"))
                gr.Markdown("A chamada é manual e analisa somente esta avaliação. A chave não é gravada no código nem no repositório.")
            single_btn = gr.Button("Executar agente", variant="primary")
            single_md = gr.Markdown()
            single_json = gr.JSON(label="Saída estruturada auditável")
            llm_json = gr.Code(label="Segunda análise da LLM (opcional)", language="json")
            single_btn.click(analyze_single, inputs=[score, title, comment, api_key, model], outputs=[single_md, single_json, llm_json])
        with gr.Tab("Análise em lote"):
            max_rows = gr.Number(label="Limite de linhas (0 = todas)", value=0, precision=0)
            batch_btn = gr.Button("Processar avaliações", variant="primary")
            batch_md = gr.Markdown()
            batch_table = gr.Dataframe(label="Resultado detalhado", interactive=False)
            batch_file = gr.File(label="Baixar CSV de resultados")
            source_state = gr.Textbox(visible=False)
            batch_btn.click(analyze_uploaded, inputs=[files, max_rows], outputs=[batch_md, batch_table, batch_file, source_state])
        with gr.Tab("Validação e auditoria"):
            validate_btn = gr.Button("Executar cinco testes funcionais", variant="primary")
            validation_md = gr.Markdown()
            validation_table = gr.Dataframe(label="Evidências dos testes", interactive=False)
            validate_btn.click(run_validation, outputs=[validation_md, validation_table])
            gr.Markdown("""
### Controles e limites
- O agente não aplica penalidades a vendedores e não conclui fraude ou responsabilidade.
- Alegações de autenticidade, fraude ou segurança exigem revisão humana.
- Divergências entre nota e comentário são sinalizadas.
- Comentários ausentes são tratados como informação insuficiente.
- A análise local não envia dados para serviços externos.
- A integração LLM é opcional, manual e limitada à avaliação selecionada.

### Auditoria
Repositório: https://github.com/vitor-souza-ime/olist-agent

A amostra de 100 avaliações citada em demonstração anterior não foi recuperada com registros individuais e critérios de seleção auditáveis. Portanto, seus números não são tratados como resultados confirmados nesta versão. Os cinco testes são casos sintéticos controlados para validar o funcionamento do fluxo.
""")
        gr.Markdown("---\n**Fluxo:** entrada → interpretação → classificação → severidade → recomendação → revisão humana quando crítica → saída estruturada.")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, show_error=True, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="cyan"))


if __name__ == "__main__":
    launch()
