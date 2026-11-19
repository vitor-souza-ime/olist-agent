import pandas as pd
from agent import analyze_review, answer_manager_question

def test_delivery_comment_is_tagged():
    r=analyze_review({"review_score":1,"review_comment_message":"Ainda não recebi minha mercadoria"})
    assert "Entrega e logística" in r["themes"]

def test_missing_item_and_damage_can_be_multilabel():
    r=analyze_review({"review_score":1,"review_comment_message":"Caixa chegou violada. Produto faltando peças e com marcas de uso."})
    assert "Pedido incompleto / item ausente" in r["themes"]
    assert "Embalagem" in r["themes"]

def test_blank_text_is_not_interpreted():
    r=analyze_review({"review_score":3,"review_comment_message":""})
    assert r["themes"]=="Sem comentário textual"
    assert r["sentiment"]=="Não determinado"

def test_manager_summary_counts_negative_reviews():
    df=pd.DataFrame([{"review_score":1,"review_comment_message":"Não recebi o produto"},{"review_score":5,"review_comment_message":"Produto excelente"}])
    summary=answer_manager_question(df)
    assert summary["negative_reviews"]==1
    assert summary["top_lexical_causes"][0]["theme"]=="Entrega e logística"
