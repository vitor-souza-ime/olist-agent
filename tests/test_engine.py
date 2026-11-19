import pandas as pd

from olist_agent.engine import analyze_review, analyze_batch, build_executive_summary


def test_incomplete_order_is_high_severity():
    r = analyze_review({"review_score": 1, "review_comment_message": "Comprei oito fronhas, mas chegaram apenas quatro."})
    assert r["theme"] == "incomplete_order"
    assert r["severity"] == "Alta"


def test_negative_text_overrides_positive_score_and_flags_discrepancy():
    r = analyze_review({"review_score": 5, "review_comment_message": "Era para chegar ontem, mas até hoje não recebi."})
    assert r["theme"] == "delivery"
    assert r["sentiment"] == "Negativo"
    assert r["score_text_discrepancy"] is True


def test_critical_authenticity_allegation_requires_human_review():
    r = analyze_review({"review_score": 1, "review_comment_message": "O cartucho chegou embolorado e parece falsificado."})
    assert r["theme"] == "critical_integrity_safety"
    assert r["severity"] == "Crítica"
    assert r["needs_human_review"] is True


def test_positive_review_is_not_flagged():
    r = analyze_review({"review_score": 5, "review_comment_message": "Chegou antes do prazo e corresponde ao anunciado."})
    assert r["theme"] == "positive_experience"
    assert r["sentiment"] == "Positivo"
    assert r["severity"] == "Baixa"
    assert r["needs_human_review"] is False


def test_empty_comment_is_insufficient_not_invented():
    r = analyze_review({"review_score": 3, "review_comment_message": ""})
    assert r["theme"] == "no_comment"
    assert r["sentiment"] == "Não determinado"
    assert r["severity"] == "Indeterminada"


def test_batch_summary_counts_rows_and_themes():
    df = pd.DataFrame([
        {"review_score": 1, "review_comment_message": "Faltou um item."},
        {"review_score": 5, "review_comment_message": "Excelente, recomendo."},
    ])
    result = analyze_batch(df)
    summary = build_executive_summary(result)
    assert summary["total"] == 2
    assert summary["negative"] == 1
    assert summary["top_causes"][0]["count"] >= 1
