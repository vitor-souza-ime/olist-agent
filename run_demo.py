from pathlib import Path
import pandas as pd
from olist_agent.engine import analyze_batch, build_executive_summary

path = Path(__file__).parent / "data" / "demo_reviews.csv"
reviews = pd.read_csv(path)
results = analyze_batch(reviews)
summary = build_executive_summary(results)
print("OLIST INTELLIGENT REVIEWS — DEMONSTRAÇÃO")
print(f"Avaliações sintéticas: {summary['total']}")
print(f"Nota média da amostra demonstrativa: {summary['average_score']}")
print(f"Negativas: {summary['negative']} | Críticas: {summary['critical']} | Revisão humana obrigatória: {summary['human_review']}")
print("\nClassificações:")
print(results[["review_id", "review_score", "sentiment", "theme_label", "severity", "needs_human_review"]].to_string(index=False))
print("\nATENÇÃO: estes registros são sintéticos e não representam a base Olist.")
