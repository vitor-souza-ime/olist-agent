from pathlib import Path

import pandas as pd


def test_real_demo_reviews_file_is_present_and_auditable():
    path = Path(__file__).resolve().parents[1] / "data" / "olist_real_demo_reviews.csv"
    reviews = pd.read_csv(path)
    assert len(reviews) == 18
    assert reviews["review_id"].notna().all()
    assert reviews["review_id"].is_unique
