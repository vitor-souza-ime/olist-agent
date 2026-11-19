"""Data loading, validation and optional enrichment for Olist CSV files."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
import zipfile

import pandas as pd


def read_csv_bytes(payload: bytes, filename: str) -> pd.DataFrame:
    compression = "gzip" if filename.lower().endswith(".gz") else "infer"
    return pd.read_csv(BytesIO(payload), compression=compression, low_memory=False)


def validate_reviews(df: pd.DataFrame) -> dict[str, Any]:
    missing = []
    score_col = "review_score" if "review_score" in df.columns else ("score" if "score" in df.columns else None)
    if score_col is None:
        missing.append("review_score (ou score)")
    text_col = "review_comment_message" if "review_comment_message" in df.columns else ("comment" if "comment" in df.columns else None)
    title_col = "review_comment_title" if "review_comment_title" in df.columns else ("title" if "title" in df.columns else None)
    if text_col is None and title_col is None:
        missing.append("review_comment_message (ou comment/title)")
    score = pd.to_numeric(df[score_col], errors="coerce") if score_col else pd.Series(dtype=float)
    if text_col and title_col:
        message_blank = df[text_col].fillna("").astype(str).str.strip().eq("")
        title_blank = df[title_col].fillna("").astype(str).str.strip().eq("")
        comment_missing = message_blank & title_blank
    elif text_col:
        comment_missing = df[text_col].isna() | df[text_col].astype(str).str.strip().eq("")
    elif title_col:
        comment_missing = df[title_col].isna() | df[title_col].astype(str).str.strip().eq("")
    else:
        comment_missing = pd.Series([True] * len(df))
    return {
        "valid": len(missing) == 0,
        "missing_columns": sorted(set(missing)),
        "rows": int(len(df)),
        "duplicate_review_ids": int(df["review_id"].duplicated().sum()) if "review_id" in df.columns else 0,
        "invalid_scores": int((~score.between(1, 5) & score.notna()).sum()) if len(score) else 0,
        "missing_scores": int(score.isna().sum()) if len(score) else int(len(df)),
        "missing_comments": int(comment_missing.sum()),
    }


def enrich_reviews(
    reviews: pd.DataFrame,
    orders: pd.DataFrame | None = None,
    items: pd.DataFrame | None = None,
    products: pd.DataFrame | None = None,
    sellers: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Join optional Olist tables without multiplying a review by item count."""
    out = reviews.copy()
    if orders is not None and "order_id" in out.columns and "order_id" in orders.columns:
        order_cols = [c for c in [
            "order_id", "order_purchase_timestamp", "order_delivered_customer_date",
            "order_estimated_delivery_date", "order_status"
        ] if c in orders.columns]
        out = out.merge(orders[order_cols].drop_duplicates("order_id"), on="order_id", how="left")
    if items is not None and "order_id" in out.columns and "order_id" in items.columns:
        item_cols = [c for c in ["order_id", "seller_id", "product_id"] if c in items.columns]
        item_subset = items[item_cols].copy()
        if products is not None and "product_id" in item_subset.columns and "product_id" in products.columns:
            pcols = [c for c in ["product_id", "product_category_name"] if c in products.columns]
            item_subset = item_subset.merge(products[pcols].drop_duplicates("product_id"), on="product_id", how="left")
        if sellers is not None and "seller_id" in item_subset.columns and "seller_id" in sellers.columns:
            scols = [c for c in ["seller_id", "seller_city", "seller_state"] if c in sellers.columns]
            item_subset = item_subset.merge(sellers[scols].drop_duplicates("seller_id"), on="seller_id", how="left")
        group_cols = [c for c in ["product_category_name", "seller_id", "seller_city", "seller_state"] if c in item_subset.columns]
        if group_cols:
            grouped = item_subset.groupby("order_id", as_index=False).agg({
                c: lambda s: ", ".join(sorted(set(s.dropna().astype(str)))) for c in group_cols
            })
            out = out.merge(grouped, on="order_id", how="left")
    return out


def load_zip_dataset(payload: bytes) -> dict[str, pd.DataFrame]:
    """Read Olist CSV or CSV.GZ files from a ZIP upload."""
    tables: dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(BytesIO(payload)) as archive:
        for name in archive.namelist():
            low = name.lower()
            if low.endswith(".csv") or low.endswith(".csv.gz"):
                basename = Path(name).name.lower()
                key = basename.replace(".csv.gz", "").replace(".csv", "")
                tables[key] = pd.read_csv(archive.open(name), compression="gzip" if low.endswith(".gz") else "infer", low_memory=False)
    return tables
