"""Core deterministic triage engine for Olist Intelligent Reviews.

This module deliberately separates evidence-based rules from optional LLM
assistance. It never treats a rule score as a calibrated probability.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

import pandas as pd


THEME_LABELS = {
    "critical_integrity_safety": "Autenticidade, fraude ou segurança",
    "incomplete_order": "Pedido incompleto / item ausente",
    "delivery": "Entrega e logística",
    "product_mismatch": "Produto divergente do anúncio",
    "product_quality": "Qualidade ou defeito do produto",
    "packaging": "Embalagem e acondicionamento",
    "customer_service": "Atendimento e comunicação",
    "payment": "Pagamento e estorno",
    "positive_experience": "Experiência positiva",
    "other": "Outro / não classificado",
    "no_comment": "Sem comentário textual",
}

THEME_AREAS = {
    "critical_integrity_safety": "Qualidade, Compliance e Gestão de Sellers",
    "incomplete_order": "Operações e Expedição",
    "delivery": "Logística e Customer Service",
    "product_mismatch": "Catálogo, Produto e Gestão de Sellers",
    "product_quality": "Qualidade e Gestão de Sellers",
    "packaging": "Operações e Expedição",
    "customer_service": "Customer Service",
    "payment": "Financeiro e Pagamentos",
    "positive_experience": "Experiência do Cliente",
    "other": "Experiência do Cliente",
    "no_comment": "Experiência do Cliente",
}

RECOMMENDATIONS = {
    "critical_integrity_safety": (
        "Preservar o relato e os dados do pedido; abrir investigação de qualidade/autenticidade "
        "ou segurança; verificar lote e fornecedor. Não concluir fraude nem aplicar sanção sem "
        "apuração humana."
    ),
    "incomplete_order": (
        "Conferir os itens registrados no pedido contra separação, embalagem e expedição; "
        "verificar divergências de quantidade e recorrência por operação ou seller."
    ),
    "delivery": (
        "Comparar prazo prometido, eventos de rastreamento e data efetiva; verificar a rota e "
        "o parceiro logístico e avaliar comunicação proativa ao cliente."
    ),
    "product_mismatch": (
        "Comparar o item recebido com o anúncio, SKU, descrição e imagens; revisar cadastro "
        "do catálogo e processo de picking antes de atribuir responsabilidade."
    ),
    "product_quality": (
        "Verificar evidências do defeito, lote e fornecedor; avaliar inspeção amostral e "
        "recorrência por categoria/produto. Encaminhar risco de segurança para revisão humana."
    ),
    "packaging": (
        "Inspecionar padrão de embalagem, proteção e integridade na expedição; cruzar com "
        "ocorrências de transporte antes de definir a causa."
    ),
    "customer_service": (
        "Verificar histórico de contato, tempo de resposta e cumprimento do SLA; encaminhar "
        "casos sem retorno para a fila de Customer Service."
    ),
    "payment": (
        "Conciliar transações, cobranças e estornos com o registro financeiro; não prometer "
        "reembolso sem confirmação do sistema e validação da política."
    ),
    "positive_experience": (
        "Registrar o aspecto positivo como prática a preservar e acompanhar se o padrão se "
        "repete em outras avaliações da mesma categoria ou jornada."
    ),
    "other": (
        "Encaminhar para triagem de qualidade; solicitar contexto adicional quando necessário "
        "e evitar atribuir uma causa sem evidência textual."
    ),
    "no_comment": (
        "Não inferir a causa da nota. Manter a avaliação como informação insuficiente e, se "
        "necessário, buscar contexto em fontes operacionais autorizadas."
    ),
}

# Phrases are normalized (lowercase, no accents) before matching.
KEYWORDS = {
    "critical_integrity_safety": [
        "falsificad", "falso", "pirata", "fraude", "golpe", "roubaram", "roubo",
        "produto adulterado", "contaminad", "embolorado", "mofado", "risco a saude",
        "risco de seguranca", "perigoso", "curto circuito", "pegou fogo", "machucou",
        "discriminacao", "racismo", "ameaca", "vazamento de dados",
    ],
    "incomplete_order": [
        "faltou", "faltando", "nao veio", "nao vieram", "veio apenas", "chegaram apenas",
        "chegou apenas", "pedido incompleto", "item ausente", "peca ausente", "metade",
        "quantidade menor", "vieram so", "veio so",
    ],
    "delivery": [
        "atras", "demorou", "demora", "prazo", "entrega", "transportadora", "transport",
        "rastreio", "nao recebi", "nao chegou", "extravi", "perdido", "nao foi entregue",
        "ainda nao chegou", "entregue depois",
    ],
    "product_mismatch": [
        "produto errado", "produto diferente", "veio errado", "modelo diferente", "nao corresponde",
        "diferente do anunciado", "divergente", "nao era o que comprei", "anuncio diferente",
    ],
    "product_quality": [
        "defeito", "quebrado", "danificado", "avariado", "nao funciona", "parou de funcionar",
        "estragado", "descosturado", "manchado", "baixa qualidade", "qualidade ruim",
        "peca quebrada", "veio quebrado",
    ],
    "packaging": [
        "embalagem", "amassado", "mal embalado", "sem protecao", "caixa aberta",
        "embalagem aberta", "violado", "pacote rasgado",
    ],
    "customer_service": [
        "atendimento", "suporte", "nao responderam", "nao responde", "sem retorno",
        "vendedor nao respondeu", "ninguem respondeu", "falta de comunicacao",
    ],
    "payment": [
        "cobrado duas vezes", "cobranca duplicada", "pagamento", "estorno", "reembolso",
        "cartao", "boleto", "cobraram", "cobrado a mais",
    ],
}

POSITIVE_PHRASES = [
    "chegou antes", "entrega rapida", "muito rapido", "rapido e bem embalado",
    "corresponde ao anunciado", "produto excelente", "excelente", "otimo", "otima",
    "perfeito", "perfeita", "recomendo", "muito bom", "muito boa", "satisfeito",
    "satisfeita", "adorei", "amei", "funciona perfeitamente",
]
NEGATIVE_PHRASES = [
    "nao recebi", "nao chegou", "atras", "faltou", "faltando", "quebrado", "defeito",
    "nao funciona", "falsificad", "fraude", "ruim", "péssimo", "pessimo", "horrivel",
    "decepcion", "errado", "danificado", "embolorado", "mofado", "cobrado duas vezes",
    "sem retorno", "nao responderam", "nao corresponde",
]


def normalize_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text


def _find_matches(text: str, phrases: list[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase in text]


def _get_theme(text: str) -> tuple[str, list[str]]:
    if not text:
        return "no_comment", []
    # Explicitly positive wording should not be misread as a logistics/product complaint.
    positive_hits = _find_matches(text, POSITIVE_PHRASES)
    negative_hits = _find_matches(text, NEGATIVE_PHRASES)
    if positive_hits and not negative_hits:
        return "positive_experience", positive_hits
    # Critical safety/integrity allegations have precedence and always require review.
    for theme in [
        "critical_integrity_safety", "incomplete_order", "delivery", "product_mismatch",
        "product_quality", "packaging", "customer_service", "payment",
    ]:
        hits = _find_matches(text, KEYWORDS[theme])
        if hits:
            return theme, hits
    if _find_matches(text, POSITIVE_PHRASES):
        return "positive_experience", _find_matches(text, POSITIVE_PHRASES)
    return "other", []


def analyze_review(row: dict[str, Any] | pd.Series) -> dict[str, Any]:
    """Classify one review and return an auditable structured record."""
    data = dict(row)
    title = data.get("review_comment_title", data.get("title", ""))
    comment = data.get("review_comment_message", data.get("comment", ""))
    title_text = "" if pd.isna(title) else str(title)
    comment_text = "" if pd.isna(comment) else str(comment)
    full_text = " ".join(part.strip() for part in [title_text, comment_text] if part and part.strip())
    normalized = normalize_text(full_text)

    raw_score = data.get("review_score", data.get("score", None))
    try:
        score = int(float(raw_score)) if raw_score is not None and str(raw_score).strip() else None
    except (TypeError, ValueError):
        score = None
    if score is not None and score not in range(1, 6):
        score = None

    review_id = data.get("review_id") or data.get("id") or ""
    order_id = data.get("order_id") or ""
    theme, matched_terms = _get_theme(normalized)

    if not normalized:
        sentiment = "Não determinado"
        severity = "Indeterminada"
        discrepancy = False
        discrepancy_reason = "Sem comentário textual; a nota isolada não explica a causa."
    else:
        negative_hits = _find_matches(normalized, NEGATIVE_PHRASES)
        positive_hits = _find_matches(normalized, POSITIVE_PHRASES)
        # Text takes precedence when it clearly contradicts the numeric score.
        if negative_hits:
            sentiment = "Negativo"
        elif positive_hits:
            sentiment = "Positivo"
        elif score is not None and score <= 2:
            sentiment = "Negativo"
        elif score is not None and score >= 4:
            sentiment = "Positivo"
        else:
            sentiment = "Neutro"

        discrepancy = bool(
            score is not None and ((score >= 4 and sentiment == "Negativo") or
                                   (score <= 2 and sentiment == "Positivo"))
        )
        discrepancy_reason = (
            f"Nota {score} diverge do teor textual ({sentiment.lower()}); revisar a avaliação."
            if discrepancy else ""
        )
        if theme == "critical_integrity_safety":
            severity = "Crítica"
        elif sentiment == "Positivo":
            severity = "Baixa"
        elif theme in {"incomplete_order", "delivery", "product_mismatch", "product_quality", "payment"} or (score is not None and score <= 2):
            severity = "Alta"
        else:
            severity = "Média"

    needs_human_review = theme == "critical_integrity_safety"
    human_reason = (
        "Alegação potencialmente crítica (fraude, autenticidade ou segurança); requer apuração humana."
        if needs_human_review else ""
    )
    if discrepancy and not needs_human_review:
        human_reason = "Divergência entre nota e comentário; recomenda-se conferência humana."

    evidence = full_text if full_text else "Comentário vazio ou ausente."
    category = data.get("product_category_name", data.get("category", ""))
    seller = data.get("seller_id", "")
    date = data.get("review_creation_date", data.get("date", ""))

    return {
        "review_id": str(review_id),
        "order_id": str(order_id),
        "review_score": score,
        "comment": full_text,
        "sentiment": sentiment,
        "theme": theme,
        "theme_label": THEME_LABELS[theme],
        "severity": severity,
        "responsible_area": THEME_AREAS[theme],
        "recommendation": RECOMMENDATIONS[theme],
        "needs_human_review": needs_human_review,
        "human_review_reason": human_reason,
        "score_text_discrepancy": discrepancy,
        "discrepancy_reason": discrepancy_reason,
        "matched_terms": ", ".join(matched_terms),
        "evidence": evidence,
        "product_category_name": str(category) if pd.notna(category) else "",
        "seller_id": str(seller) if pd.notna(seller) else "",
        "review_creation_date": str(date) if pd.notna(date) else "",
    }


def analyze_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze every row without sending review text to an external service."""
    if df is None or df.empty:
        return pd.DataFrame()
    records = [analyze_review(row) for row in df.to_dict(orient="records")]
    return pd.DataFrame(records)


def build_executive_summary(results: pd.DataFrame) -> dict[str, Any]:
    if results is None or results.empty:
        return {
            "total": 0, "average_score": None, "negative": 0, "critical": 0,
            "human_review": 0, "no_comment": 0, "top_causes": [],
        }
    scores = pd.to_numeric(results["review_score"], errors="coerce")
    counts = Counter(results["theme"].tolist())
    top_causes = [
        {"theme": key, "label": THEME_LABELS.get(key, key), "count": value,
         "share_pct": round(value / len(results) * 100, 1),
         "recommendation": RECOMMENDATIONS.get(key, RECOMMENDATIONS["other"]),
         "area": THEME_AREAS.get(key, "Experiência do Cliente")}
        for key, value in counts.most_common(5)
    ]
    return {
        "total": int(len(results)),
        "average_score": round(float(scores.mean()), 2) if scores.notna().any() else None,
        "negative": int((results["sentiment"] == "Negativo").sum()),
        "critical": int((results["severity"] == "Crítica").sum()),
        "human_review": int(results["needs_human_review"].sum()),
        "no_comment": int((results["theme"] == "no_comment").sum()),
        "top_causes": top_causes,
    }
