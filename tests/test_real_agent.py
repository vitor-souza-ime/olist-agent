import pandas as pd

from app_real import analyze_dataset, answer_manager, classify_review


def test_real_review_classifier_flags_incomplete_order():
    result = classify_review(
        1, "",
        "Recebi metade do pedido e na nota fiscal consta toda mercadoria."
    )
    assert result["primary_theme"] == "Pedido incompleto / item ausente"
    assert result["severity"] == "Alta"


def test_real_review_classifier_detects_delivery_and_refund_signals():
    result = classify_review(
        1, "",
        "O pedido não foi entregue e quero meu dinheiro de volta."
    )
    assert "Entrega e logística" in result["themes"]
    assert "Devolução, estorno e pagamento" in result["themes"]


def test_critical_claim_requires_human_review():
    result = classify_review(1, "", "O produto parece falsificado e apresenta risco de segurança.")
    assert result["human_review"] is True
    assert result["severity"] == "Crítica"


def test_empty_review_does_not_infer_a_problem():
    result = classify_review(1, "", "")
    assert result["primary_theme"] == "Outro / sem comentário"
    assert result["severity"] == "Indeterminada"


def test_real_dataset_analysis_and_manager_answer_use_computed_counts():
    tables = {
        "reviews": pd.DataFrame([
            {"review_id":"r1","order_id":"o1","review_score":1,"review_comment_title":"","review_comment_message":"Meu produto não foi entregue."},
            {"review_id":"r2","order_id":"o2","review_score":1,"review_comment_title":"","review_comment_message":"Pedido incompleto, faltou um item."},
            {"review_id":"r3","order_id":"o3","review_score":1,"review_comment_title":"","review_comment_message":"Produto com defeito, não funciona."},
            {"review_id":"r4","order_id":"o4","review_score":1,"review_comment_title":"","review_comment_message":"Não recebi resposta e não recebi o estorno."},
            {"review_id":"r5","order_id":"o5","review_score":5,"review_comment_title":"","review_comment_message":"Excelente, recomendo."},
        ]),
        "orders": pd.DataFrame([
            {"order_id":"o1","order_delivered_customer_date":"2018-01-10","order_estimated_delivery_date":"2018-01-05"},
            {"order_id":"o2","order_delivered_customer_date":"2018-01-04","order_estimated_delivery_date":"2018-01-05"},
            {"order_id":"o3","order_delivered_customer_date":"2018-01-04","order_estimated_delivery_date":"2018-01-05"},
            {"order_id":"o4","order_delivered_customer_date":"2018-01-04","order_estimated_delivery_date":"2018-01-05"},
            {"order_id":"o5","order_delivered_customer_date":"2018-01-04","order_estimated_delivery_date":"2018-01-05"},
        ])
    }
    analysis = analyze_dataset(tables)
    answer = answer_manager("Quais são os três problemas mais importantes?", analysis)
    assert analysis["unique_reviews"] == 5
    assert analysis["low_text"] == 4
    assert "Entrega e cumprimento do pedido" in answer
    assert "triagem lexical" in answer
