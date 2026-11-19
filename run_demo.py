from pathlib import Path
from app_real import load_zip, analyze_dataset, answer_manager, classify_review

ROOT = Path(__file__).parent
dataset = ROOT / "data" / "olist_public_dataset.zip"
if not dataset.exists():
    raise SystemExit("Baixe o ZIP do Kaggle e salve-o em data/olist_public_dataset.zip.")

tables = load_zip(dataset.read_bytes())
summary = analyze_dataset(tables)

def br_int(value):
    return f"{int(value):,}".replace(",", ".")

def br_num(value, digits=2):
    return f"{float(value):.{digits}f}".replace(".", ",")

print("OLIST INTELLIGENT REVIEWS — DEMONSTRAÇÃO COM DADOS REAIS")
print(f"Linhas originais: {br_int(summary['raw_rows'])}")
print(f"Reviews únicos: {br_int(summary['unique_reviews'])}")
print(f"Nota média: {br_num(summary['average_score'])}")
print(f"Notas 1–2: {br_int(summary['low_reviews'])} ({br_num(summary['low_share'], 1)}%)")
print()
question = "Quais são os três problemas mais importantes encontrados nas avaliações e o que a Olist deveria fazer?"
print("PERGUNTA DO GESTOR")
print(question)
print()
print(answer_manager(question, summary))

review_id = "96ab47052a57bbfbba3b48d4203cf1f3"
review = summary["reviews"].loc[summary["reviews"]["review_id"] == review_id].iloc[0]
result = classify_review(review["review_score"], review["review_comment_title"], review["review_comment_message"])
print()
print("ANÁLISE INDIVIDUAL DE REVIEW REAL")
for key in ["review_score", "sentiment", "primary_theme", "severity", "context", "recommendation"]:
    print(f"{key}: {result[key]}")
