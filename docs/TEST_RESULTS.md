# Resultados de validação — Olist Intelligent Reviews

Data da execução: 19/11/2026.

## Testes automatizados locais

Comando: `python -m pytest -q`.

Resultado: 17 testes aprovados na versão local atualizada.

## Execução sobre o dataset Olist fornecido

- Linhas originais de Order_Reviews: 99.224.
- `review_id` únicos: 98.410.
- Linhas excedentes removidas por ID repetido: 814.
- Nota média: 4,09/5.
- Notas 1–2: 14.396 (14,6%).
- Comentários de notas 1–2 com texto: 10.861.
- Comentários com ao menos um padrão lexical: 5.719 (52,7%).
- Grupos prioritários: entrega/cumprimento (3.970), produto/qualidade/divergência (1.255), pós-venda (852).

## Limitações

- A segunda opinião OpenRouter requer API key e não foi executada nesta validação.
- Não foi medida acurácia semântica contra rótulos de referência produzidos por especialistas.
- Não foram medidos ganhos de produtividade, CSAT, redução de custos ou impacto financeiro em produção.
- As métricas descrevem o dataset histórico, não a situação atual da operação Olist.
