"""Olist Intelligent Reviews — versão com o dataset real da Olist."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import json
import os
import re
import unicodedata
import zipfile

import gradio as gr
import numpy as np
import pandas as pd
import requests
from olist_agent.llm import analyze_with_openrouter

ROOT = Path(__file__).parent
DEFAULT_ZIP = ROOT / "data" / "olist_public_dataset.zip"

PATTERNS = {
    "delivery": [
        r"\bnao recebi o produto\b", r"\bnao recebi meu pedido\b", r"\bnao recebi a mercadoria\b",
        r"\bnao foi entregue\b", r"\bnao chegou\b", r"\bnao entreg\w*\b", r"\batras\w*\b",
        r"\bdemor\w*\b", r"\bprazo de entrega\b", r"\bcorreios\b", r"\btransportadora\b",
        r"\bextravi\w*\b", r"\bpassou do prazo\b", r"\bfora do prazo\b", r"\bpedido nao chegou\b",
    ],
    "incomplete_order": [
        r"\bfaltando\b", r"\bfaltou\b", r"\bpedido incompleto\b", r"\bveio apenas\b",
        r"\brecebi apenas\b", r"\brecebi somente\b", r"\bveio somente\b", r"\bvieram apenas\b",
        r"\bentrega parcial\b", r"\bparte do pedido\b", r"\bnao veio\b", r"\bnao vieram\b",
        r"\brecebi metade\b", r"\bquantidade menor\b",
    ],
    "customer_service": [
        r"\bsem resposta\b", r"\bnao responde\w*\b", r"\bnao responderam\b",
        r"\bnao recebi resposta\b", r"\bsem retorno\b", r"\bnao tive retorno\b",
        r"\bninguem responde\w*\b", r"\bnao consigo contato\b", r"\bnao consegui contato\b",
        r"\bnao entraram em contato\b", r"\bnao me deram retorno\b", r"\bnao obtive resposta\b",
        r"\bpessimo atendimento\b", r"\batendimento ruim\b", r"\bsem suporte\b",
    ],
    "payment_refund": [
        r"\breembolso\b", r"\bestorno\b", r"\bdevolucao\b", r"\bmeu dinheiro\b",
        r"\bdinheiro de volta\b", r"\bquero meu dinheiro\b", r"\bcobranca duplicada\b",
        r"\bcobrado duas vezes\b", r"\bcobrado a mais\b", r"\bnao devolveram\b",
        r"\bcredito referente\b", r"\bvoucher\b", r"\bnao consigo utilizar o credito\b",
    ],
    "product_quality": [
        r"\bdefeit\w*\b", r"\bquebrad\w*\b", r"\bnao funciona\b", r"\bparou de funcionar\b",
        r"\bnao lig\w*\b", r"\bqualidade do produto\b", r"\bpessima qualidade\b",
        r"\bbaixa qualidade\b", r"\bqualidade ruim\b", r"\bqualidade deixa a desejar\b",
        r"\bdanificad\w*\b", r"\bavariad\w*\b", r"\bestragad\w*\b", r"\bmal feit\w*\b",
        r"\bdescostur\w*\b", r"\bvaz\w*\b", r"\bnao presta\b",
    ],
    "product_mismatch": [
        r"\bveio errado\b", r"\bproduto errado\b", r"\bpedido errado\b", r"\bmodelo diferente\b",
        r"\bcor diferente\b", r"\btamanho diferente\b", r"\bdiferente do anunciado\b",
        r"\bnao corresponde\b", r"\bnao era o que\b", r"\bdiferente da foto\b",
        r"\bdiferente do que\b", r"\bnao condiz com o anuncio\b", r"\bimagem nao condiz\b",
        r"\banuncio nao foi claro\b",
    ],
    "packaging": [
        r"\bembalagem\b", r"\bcaixa amassad\w*\b", r"\bcaixa aberta\b", r"\bmal embalad\w*\b",
        r"\bpacote rasgad\w*\b", r"\bsem protecao\b",
    ],
    "critical_integrity_safety": [
        r"\bfalsificad\w*\b", r"\bpirat\w*\b", r"\bfraude\b", r"\bgolpe\b",
        r"\bcontaminad\w*\b", r"\bembolorad\w*\b", r"\bmofad\w*\b",
        r"\brisco a saude\b", r"\brisco de seguranca\b", r"\bpegou fogo\b",
        r"\bcurto circuito\b", r"\bmachucou\b", r"\bperigoso\b", r"\bvazamento de dados\b",
        r"\bracismo\b", r"\bdiscriminacao\b",
    ],
}
COMPILED = {k: re.compile("|".join(f"(?:{p})" for p in v)) for k, v in PATTERNS.items()}
LABELS = {
    "delivery": "Entrega e logística",
    "incomplete_order": "Pedido incompleto / item ausente",
    "customer_service": "Atendimento e comunicação",
    "payment_refund": "Devolução, estorno e pagamento",
    "product_quality": "Qualidade ou defeito do produto",
    "product_mismatch": "Produto divergente do anúncio",
    "packaging": "Embalagem e acondicionamento",
    "critical_integrity_safety": "Autenticidade, fraude ou segurança",
}
ACTIONS = {
    "Entrega e cumprimento do pedido": "Conferir rastreamento, comprovante de entrega, separação e comunicação; tratar divergências de entrega parcial.",
    "Produto: qualidade, defeito ou divergência": "Cruzar defeitos e divergências com SKU, anúncio, imagens, lote e fornecedor; priorizar inspeção.",
    "Pós-venda: atendimento, devolução e pagamento": "Revisar tickets, tempo de resposta, cancelamentos, devoluções e conciliação de estornos.",
}
RECOMMENDATIONS = {
    "delivery": "Conferir prazo prometido, eventos de rastreamento e comprovante de entrega; investigar rota e parceiro logístico.",
    "incomplete_order": "Comparar itens e quantidades com nota fiscal, picking, packing e expedição.",
    "customer_service": "Consultar histórico de contatos, tickets e SLA; encaminhar ausência de retorno à fila responsável.",
    "payment_refund": "Conciliar pedido, pagamento, cancelamento, crédito, devolução e estorno antes de orientar o cliente.",
    "product_quality": "Verificar defeito relatado, lote, fornecedor e instruções de uso; avaliar recorrência por produto.",
    "product_mismatch": "Comparar SKU, descrição, imagens e atributos do anúncio com o item enviado.",
    "packaging": "Inspecionar embalagem e proteção; cruzar avarias com expedição e transporte.",
    "critical_integrity_safety": "Preservar o relato e abrir apuração humana; não concluir irregularidade sem evidência independente.",
    "other": "Encaminhar para triagem de qualidade; não atribuir causa sem evidência textual suficiente.",
    "no_comment": "Não inferir a causa a partir da nota isolada; buscar contexto em fontes autorizadas.",
}

def normalize(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = unicodedata.normalize("NFKD", str(value).lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip()

def br_int(value):
    return f"{int(value):,}".replace(",", ".")

def br_num(value, digits=1):
    return f"{float(value):.{digits}f}".replace(".", ",")

def load_zip(payload: bytes):
    wanted = {
        "olist_order_reviews_dataset.csv": "reviews",
        "olist_orders_dataset.csv": "orders",
        "olist_order_items_dataset.csv": "items",
        "olist_products_dataset.csv": "products",
        "olist_sellers_dataset.csv": "sellers",
    }
    tables = {}
    with zipfile.ZipFile(BytesIO(payload)) as z:
        names = {Path(n).name.lower(): n for n in z.namelist()}
        for filename, key in wanted.items():
            if filename in names:
                with z.open(names[filename]) as stream:
                    tables[key] = pd.read_csv(stream, low_memory=False)
    if "reviews" not in tables:
        raise ValueError("O ZIP não contém olist_order_reviews_dataset.csv.")
    return tables

def analyze_dataset(tables):
    raw = tables["reviews"]
    reviews = raw.drop_duplicates("review_id", keep="first").copy()
    title = reviews.get("review_comment_title", pd.Series([""] * len(reviews))).fillna("").astype(str)
    message = reviews.get("review_comment_message", pd.Series([""] * len(reviews))).fillna("").astype(str)
    reviews["text"] = (title.str.strip() + " " + message.str.strip()).str.strip()
    reviews["norm"] = reviews["text"].map(normalize)
    reviews["has_text"] = reviews["norm"].ne("")
    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
    for theme, pattern in COMPILED.items():
        reviews[f"lex_{theme}"] = reviews["norm"].str.contains(pattern, na=False)

    low = reviews[(reviews["review_score"] <= 2) & reviews["has_text"]].copy()
    groups = {
        "Entrega e cumprimento do pedido": ["delivery", "incomplete_order"],
        "Produto: qualidade, defeito ou divergência": ["product_quality", "product_mismatch"],
        "Pós-venda: atendimento, devolução e pagamento": ["customer_service", "payment_refund"],
        "Embalagem e acondicionamento": ["packaging"],
        "Autenticidade, fraude ou segurança": ["critical_integrity_safety"],
    }
    cluster_rows = []
    for label, themes in groups.items():
        mask = np.zeros(len(low), dtype=bool)
        for theme in themes:
            mask |= low[f"lex_{theme}"].to_numpy(dtype=bool)
        count = int(mask.sum())
        cluster_rows.append({"label": label, "count": count, "share_pct": round(100 * count / len(low), 1) if len(low) else 0})
    cluster_rows.sort(key=lambda x: x["count"], reverse=True)

    matched = np.zeros(len(low), dtype=bool)
    for theme in COMPILED:
        matched |= low[f"lex_{theme}"].to_numpy(dtype=bool)

    score_counts = reviews["review_score"].value_counts().sort_index()
    delivery = {}
    if "orders" in tables:
        orders = tables["orders"].copy()
        for col in ["order_delivered_customer_date", "order_estimated_delivery_date"]:
            orders[col] = pd.to_datetime(orders[col], errors="coerce")
        orders["delay_days"] = (orders["order_delivered_customer_date"] - orders["order_estimated_delivery_date"]).dt.total_seconds() / 86400
        orders["delivery_group"] = np.select(
            [orders["order_delivered_customer_date"].isna(), orders["delay_days"] > 0, orders["delay_days"] <= 0],
            ["Sem data de entrega", "Atrasado", "No prazo/antecipado"], default="Indeterminado"
        )
        joined = reviews[["review_id", "order_id", "review_score"]].merge(
            orders[["order_id", "delay_days", "delivery_group"]].drop_duplicates("order_id"),
            on="order_id", how="left"
        )
        def drow(name):
            x = joined[joined["delivery_group"] == name]
            return {
                "reviews": len(x),
                "average_score": round(float(x["review_score"].mean()), 2) if len(x) else None,
                "low_share": round(100 * float((x["review_score"] <= 2).mean()), 1) if len(x) else None
            }
        late_days = joined.loc[joined["delay_days"] > 0, "delay_days"].dropna()
        delivered = joined[joined["delivery_group"].isin(["Atrasado", "No prazo/antecipado"])]
        delivery = {
            "late": drow("Atrasado"),
            "on_time": drow("No prazo/antecipado"),
            "no_date": drow("Sem data de entrega"),
            "late_share": round(100 * float((delivered["delivery_group"] == "Atrasado").mean()), 1) if len(delivered) else None,
            "mean_late_days": round(float(late_days.mean()), 2) if len(late_days) else None,
            "median_late_days": round(float(late_days.median()), 2) if len(late_days) else None,
        }

    categories = []
    if "items" in tables and "products" in tables:
        item = tables["items"][["order_id", "product_id"]].merge(
            tables["products"][["product_id", "product_category_name"]].drop_duplicates("product_id"),
            on="product_id", how="left"
        )
        order_categories = item.groupby("order_id")["product_category_name"].apply(
            lambda s: sorted(set(s.dropna().astype(str)))
        ).reset_index(name="categories")
        exploded = reviews[["review_id", "order_id", "review_score"]].merge(order_categories, on="order_id", how="left").explode("categories")
        exploded = exploded[exploded["categories"].notna()]
        cat = exploded.groupby("categories").agg(
            associations=("review_id", "size"),
            low_reviews=("review_score", lambda x: int((x <= 2).sum())),
            low_share=("review_score", lambda x: round(100 * float((x <= 2).mean()), 1)),
        ).sort_values("low_reviews", ascending=False)
        for key, row in cat.head(8).iterrows():
            categories.append({
                "category": str(key).replace("_", " ").capitalize(),
                "associations": int(row["associations"]),
                "low_reviews": int(row["low_reviews"]),
                "low_share": float(row["low_share"]),
            })

    return {
        "raw_rows": len(raw),
        "unique_reviews": len(reviews),
        "duplicates_removed": len(raw) - len(reviews),
        "average_score": round(float(reviews["review_score"].mean()), 2),
        "score_distribution": [{"score": int(k), "count": int(v)} for k, v in score_counts.items()],
        "low_reviews": int((reviews["review_score"] <= 2).sum()),
        "low_share": round(100 * float((reviews["review_score"] <= 2).mean()), 1),
        "reviews_with_text": int(reviews["has_text"].sum()),
        "reviews_without_text": int((~reviews["has_text"]).sum()),
        "low_text": len(low),
        "matched_low_text": int(matched.sum()),
        "matched_pct": round(100 * float(matched.mean()), 1) if len(low) else 0,
        "unmatched_low_text": int(len(low) - matched.sum()),
        "clusters": cluster_rows,
        "delivery": delivery,
        "categories": categories,
        "reviews": reviews,
    }

def classify_review(score, title, comment):
    text = " ".join(x for x in [str(title or ""), str(comment or "")] if x.strip())
    norm = normalize(text)
    themes = [k for k, pattern in COMPILED.items() if pattern.search(norm)]
    if not norm:
        sentiment, severity = "Não determinado", "Indeterminada"
    else:
        neg = bool(re.search(r"\b(nao recebi|nao chegou|nao foi entregue|atras|defeit|quebrad|nao funciona|faltou|faltando|recebi metade|falta de respeito|nao gostei|nao fiquei satisfeit\w*|nao recomendo)\b", norm))
        pos = bool(re.search(r"\b(excelente|otim|perfeit|recomendo|muito bom|muito boa|satisfeit\w*|adorei|amei)\b", norm))
        if re.search(r"\bnao\s+(?:estou\s+|fiquei\s+)?(?:gostei|recomendo|satisfeit\w*)", norm):
            pos = False
        sentiment = "Misto / ambíguo" if neg and pos else ("Negativo" if neg or int(score) <= 2 else ("Positivo" if pos or int(score) >= 4 else "Neutro"))
        severity = "Crítica" if "critical_integrity_safety" in themes else ("Alta" if int(score) <= 2 else ("Baixa" if sentiment == "Positivo" else "Média"))
    priority = ["critical_integrity_safety", "delivery", "incomplete_order", "payment_refund", "customer_service", "product_quality", "product_mismatch", "packaging"]
    primary = next((x for x in priority if x in themes), "other" if norm else "no_comment")
    label = LABELS.get(primary, "Outro / sem comentário")
    context = {
        "delivery": "O comentário relata atraso ou não recebimento. Conferir prazo, rastreamento e comprovante.",
        "incomplete_order": "O relato aponta possível falta de item ou quantidade. Comparar conteúdo do pedido, nota fiscal e expedição.",
        "product_quality": "O cliente descreve falha de qualidade ou funcionamento. Verificar produto, lote e fornecedor; o relato não confirma defeito técnico.",
        "payment_refund": "O cliente menciona pagamento, devolução ou estorno. Confirmar o estado financeiro antes de orientar.",
        "customer_service": "O texto indica dificuldade de contato ou ausência de retorno. Conferir tickets e SLA.",
        "product_mismatch": "O texto sugere divergência entre item recebido e anúncio. Comparar SKU, descrição e imagens.",
        "critical_integrity_safety": "Há alegação potencialmente crítica. Encaminhar para apuração humana; não tratar como fato confirmado.",
        "packaging": "O comentário menciona embalagem ou acondicionamento. Verificar expedição e transporte.",
        "other": "Não foi identificado padrão específico; solicitar leitura humana ou semântica complementar.",
        "no_comment": "Sem comentário textual; não inferir causa a partir da nota."
    }[primary]
    return {
        "sentiment": sentiment, "primary_theme": label, "themes": [LABELS[x] for x in themes],
        "severity": severity, "context": context, "evidence": text,
        "recommendation": RECOMMENDATIONS.get(primary, RECOMMENDATIONS["other"]),
        "human_review": primary == "critical_integrity_safety"
    }

def answer_manager(question, a):
    q = normalize(question)
    if any(term in q for term in ["entrega", "atras", "prazo", "logistica"]):
        d = a.get("delivery", {})
        if d:
            late, ontime = d["late"], d["on_time"]
            return (
                "## Evidência quantitativa — entrega\n\n"
                f"- Atrasados: {br_int(late['reviews'])} reviews; nota média {br_num(late['average_score'], 2)}; "
                f"{br_num(late['low_share'])}% com nota 1 ou 2.\n"
                f"- No prazo/antecipados: {br_int(ontime['reviews'])} reviews; nota média {br_num(ontime['average_score'], 2)}; "
                f"{br_num(ontime['low_share'])}% com nota 1 ou 2.\n"
                f"- Atraso médio: {br_num(d['mean_late_days'], 2)} dias; mediana: {br_num(d['median_late_days'], 2)} dias.\n\n"
                "Associação observacional, não prova de causalidade exclusiva. Recomenda-se auditar rastreamento, comprovante de entrega e parceiros logísticos."
            )
    if "categoria" in q:
        rows = a.get("categories", [])[:5]
        return "## Categorias associadas a mais notas 1–2\n\n" + "\n".join(
            f"- {x['category']}: {br_int(x['low_reviews'])} reviews baixos em {br_int(x['associations'])} associações ({br_num(x['low_share'])}%)."
            for x in rows
        ) + "\n\nPedidos com múltiplas categorias aparecem em mais de uma associação."
    lines = [
        "## Três prioridades identificadas nas avaliações reais",
        "",
        f"Base: {br_int(a['unique_reviews'])} review_ids únicos; triagem lexical aplicada a {br_int(a['low_text'])} comentários com nota 1 ou 2.",
        ""
    ]
    for i, row in enumerate(a["clusters"][:3], 1):
        lines += [
            f"### {i}. {row['label']}",
            f"**{br_int(row['count'])} comentários ({br_num(row['share_pct'])}% dos comentários de notas 1–2 com texto).**",
            f"Ação recomendada: {ACTIONS.get(row['label'], 'Encaminhar para a área responsável e revisar a evidência textual.')}",
            ""
        ]
    lines += [
        "Os grupos são multirrótulo: um comentário pode aparecer em mais de um grupo. Os percentuais não são aditivos.",
        "A contagem é triagem lexical reproduzível, não classificação semântica validada por especialistas."
    ]
    return "\n".join(lines)

STATE = {"tables": None, "analysis": None}

def load_path(file_paths):
    paths = file_paths if isinstance(file_paths, list) else [file_paths]
    zips = [p for p in paths if p and str(p).lower().endswith(".zip")]
    if not zips:
        raise ValueError("Envie o ZIP original do dataset Olist.")
    payload = Path(zips[0]).read_bytes()
    tables = load_zip(payload)
    STATE["tables"] = tables
    STATE["analysis"] = analyze_dataset(tables)
    return dashboard_text(), groups_df(), categories_df(), "Dataset carregado e analisado."

def dashboard_text():
    a = STATE["analysis"]
    if not a:
        return "Envie o ZIP do dataset Olist para começar."
    return f"""### Painel executivo — dados reais

| Indicador | Resultado |
|---|---:|
| Linhas originais | {br_int(a['raw_rows'])} |
| Reviews únicos | {br_int(a['unique_reviews'])} |
| IDs repetidos removidos | {br_int(a['duplicates_removed'])} |
| Nota média | {br_num(a['average_score'],2)} / 5 |
| Notas 1–2 | {br_int(a['low_reviews'])} ({br_num(a['low_share'])}%) |
| Comentários de notas 1–2 com texto | {br_int(a['low_text'])} |
| Sem comentário textual | {br_int(a['reviews_without_text'])} |
| Sinais lexicais encontrados | {br_int(a['matched_low_text'])} ({br_num(a['matched_pct'])}%) |
"""

def groups_df():
    a = STATE["analysis"]
    return pd.DataFrame([{"Grupo": x["label"], "Comentários": x["count"], "Percentual": f"{br_num(x['share_pct'])}%"} for x in a["clusters"]]) if a else pd.DataFrame()

def categories_df():
    a = STATE["analysis"]
    return pd.DataFrame([{"Categoria": x["category"], "Associações": x["associations"], "Notas 1–2": x["low_reviews"], "Taxa": f"{br_num(x['low_share'])}%"} for x in a["categories"]]) if a else pd.DataFrame()

def ask(question):
    if not STATE["analysis"]:
        return "Carregue o dataset primeiro."
    return answer_manager(question, STATE["analysis"])

def review_choices():
    ids = ["96ab47052a57bbfbba3b48d4203cf1f3", "cd76397f23913425751779c775bb8499",
           "8ccb6f10802a0a4341f9a339cdc7f715", "574eb8fce37a82e08574336beddd2d2c"]
    return [(f"Review real {rid[:10]}…", rid) for rid in ids]

def load_review(review_id):
    a = STATE["analysis"]
    if not a or review_id not in set(a["reviews"]["review_id"]):
        return 3, "", ""
    row = a["reviews"].loc[a["reviews"]["review_id"] == review_id].iloc[0]
    return int(row["review_score"]), str(row.get("review_comment_title") or ""), str(row.get("review_comment_message") or "")

def run_review(score, title, comment):
    result = classify_review(score, title, comment)
    return (
        f"""### Resultado da análise

- Sentimento: **{result['sentiment']}**
- Tema principal: **{result['primary_theme']}**
- Temas adicionais: **{', '.join(result['themes']) if result['themes'] else 'nenhum padrão lexical encontrado'}**
- Severidade: **{result['severity']}**
- Revisão humana obrigatória: **{'Sim' if result['human_review'] else 'Não'}**

**Evidência literal:** {result['evidence']}

**Leitura contextual:** {result['context']}

**Recomendação:** {result['recommendation']}

*A leitura contextual é uma hipótese operacional, não confirmação da causa.*
""",
        result
    )

def run_review_with_llm(score, title, comment, api_key, model):
    markdown, result = run_review(score, title, comment)
    semantic = {"status": "segunda opinião não executada"}
    if api_key:
        try:
            semantic = analyze_with_openrouter(
                {"review_score": score, "review_comment_title": title, "review_comment_message": comment},
                api_key, model or "openai/gpt-oss-120b"
            )
        except Exception as exc:
            semantic = {"error": str(exc)}
    return markdown, result, semantic

def launch():
    with gr.Blocks(title="Olist Intelligent Reviews") as demo:
        gr.Markdown("# Olist Intelligent Reviews\n### Agente de Análise de Reviews — Fase 3\nProtótipo executado sobre o dataset real da Olist.")
        with gr.Row():
            upload = gr.File(label="ZIP do dataset Olist", file_count="multiple", file_types=[".zip"], type="filepath")
            load_btn = gr.Button("Carregar dataset", variant="primary")
        status = gr.Markdown("Base pronta para carregar.")
        with gr.Tab("Painel executivo"):
            summary = gr.Markdown(dashboard_text())
            groups = gr.Dataframe(value=groups_df(), label="Problemas identificados", interactive=False)
            cats = gr.Dataframe(value=categories_df(), label="Categorias associadas", interactive=False)
            load_btn.click(load_path, inputs=upload, outputs=[summary, groups, cats, status])
        with gr.Tab("Pergunte ao agente"):
            question = gr.Textbox(label="Pergunta do gestor", value="Quais são os três problemas mais importantes encontrados nas avaliações e o que a Olist deveria fazer?", lines=2)
            ask_btn = gr.Button("Consultar agente", variant="primary")
            answer = gr.Markdown(answer_manager(question.value, STATE["analysis"]) if STATE["analysis"] else "")
            ask_btn.click(ask, inputs=question, outputs=answer)
        with gr.Tab("Analisar avaliação real"):
            choices = review_choices()
            selected = gr.Dropdown(choices=choices, label="Selecionar review real", value=choices[0][1] if choices else None)
            load_example = gr.Button("Carregar review")
            with gr.Row():
                score = gr.Slider(1, 5, value=1, step=1, label="Nota")
                title = gr.Textbox(label="Título")
            comment = gr.Textbox(label="Comentário", lines=4)
            load_example.click(load_review, inputs=selected, outputs=[score, title, comment])
            with gr.Accordion("Segunda opinião semântica via OpenRouter (opcional)", open=False):
                api_key = gr.Textbox(label="OpenRouter API key", type="password", value=os.getenv("OPENROUTER_API_KEY", ""))
                model = gr.Textbox(label="Modelo", value=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b"))
            run_btn = gr.Button("Executar agente", variant="primary")
            result = gr.Markdown()
            result_json = gr.JSON(label="Saída estruturada")
            semantic_json = gr.JSON(label="Segunda opinião generativa (se ativada)")
            run_btn.click(run_review_with_llm, inputs=[score, title, comment, api_key, model], outputs=[result, result_json, semantic_json])
        with gr.Tab("Metodologia e auditoria"):
            gr.Markdown(
                "### Camadas de análise\n"
                "- Triagem lexical quantitativa: padrões explícitos, contagens reproduzíveis e multirrótulo.\n"
                "- Leitura contextual: hipótese operacional para cada review; não confirma causa.\n"
                "- Revisão humana: alegações críticas, ambiguidades e comentários sem correspondência lexical.\n\n"
                "### Regras\n"
                "- Uma linha por review_id único; manter a primeira ocorrência.\n"
                "- Comentário vazio não recebe causa inferida.\n"
                "- Grupos podem se sobrepor; percentuais não são aditivos.\n"
                "- O agente não autoriza reembolsos, cancelamentos ou penalidades.\n\n"
                "Fonte: Olist, Brazilian E-Commerce Public Dataset by Olist, Kaggle (2018), licença CC BY-NC-SA 4.0."
            )
        gr.Markdown("---\nRepositório: https://github.com/vitor-souza-ime/olist-agent")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False, show_error=True)

if __name__ == "__main__":
    if DEFAULT_ZIP.exists():
        try:
            STATE["tables"] = load_zip(DEFAULT_ZIP.read_bytes())
            STATE["analysis"] = analyze_dataset(STATE["tables"])
        except Exception as exc:
            print(f"Falha ao carregar dataset padrão: {exc}")
    launch()
