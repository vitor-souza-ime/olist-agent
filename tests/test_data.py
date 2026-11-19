import pandas as pd
from olist_agent.data import validate_reviews, enrich_reviews


def test_validate_reviews_accepts_olist_schema():
    df = pd.DataFrame({"review_id": ["r1"], "review_score": [5], "review_comment_message": ["bom"]})
    assert validate_reviews(df)["valid"] is True


def test_enrichment_does_not_multiply_reviews_by_order_items():
    reviews = pd.DataFrame({"order_id": ["o1"], "review_score": [1]})
    items = pd.DataFrame({"order_id": ["o1", "o1"], "seller_id": ["s1", "s2"], "product_id": ["p1", "p2"]})
    products = pd.DataFrame({"product_id": ["p1", "p2"], "product_category_name": ["cat1", "cat2"]})
    enriched = enrich_reviews(reviews, items=items, products=products)
    assert len(enriched) == 1
    assert "cat1" in enriched.loc[0, "product_category_name"]
    assert "cat2" in enriched.loc[0, "product_category_name"]


def test_validate_reviews_accepts_score_alias_and_title():
    df = pd.DataFrame({"score": [4], "title": ["bom"]})
    result = validate_reviews(df)
    assert result["valid"] is True
    assert result["missing_comments"] == 0


def test_validate_reviews_counts_empty_comment_once():
    df = pd.DataFrame({
        "review_score": [5, 1],
        "review_comment_title": [None, "Título"],
        "review_comment_message": ["", "Texto"],
    })
    assert validate_reviews(df)["missing_comments"] == 1
