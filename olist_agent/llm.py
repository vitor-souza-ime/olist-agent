"""Optional OpenRouter integration. The core agent remains usable offline."""
from __future__ import annotations

import json
import requests

SYSTEM_PROMPT = """Você é o Agente de Análise de Reviews da Olist. Analise somente a avaliação fornecida.
Retorne JSON válido com: sentiment, theme, severity, evidence, recommendation, responsible_area,
needs_human_review, human_review_reason, score_text_discrepancy, discrepancy_reason.
Classifique sentimento, tema e severidade; não invente fatos; não conclua fraude nem responsabilidade
sem apuração; alegações de fraude, autenticidade, segurança, discriminação ou risco ao consumidor
exigem revisão humana. Se o comentário estiver vazio, informe dados insuficientes. Responda em português.
"""


def analyze_with_openrouter(review: dict, api_key: str, model: str = "openai/gpt-oss-120b") -> dict:
    if not api_key:
        raise ValueError("Informe uma chave OpenRouter para habilitar a análise generativa.")
    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(review, ensure_ascii=False)},
        ],
    }
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                  "HTTP-Referer": "https://github.com/vitor-souza-ime/olist-agent",
                  "X-Title": "Olist Intelligent Reviews"},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    body = response.json()
    content = body["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return json.loads(content)
