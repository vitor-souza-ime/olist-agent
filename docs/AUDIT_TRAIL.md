# Trilha de auditoria — Olist Intelligent Reviews

- Fonte: Brazilian E-Commerce Public Dataset by Olist (Kaggle).
- Arquivo analisado: olist_order_reviews_dataset.csv fornecido pelo usuário.
- Linhas brutas: 99.224; duplicatas por review_id: 814; avaliações únicas: 98.410.
- Deduplicação: manter a primeira ocorrência de cada review_id.
- Triagem: regras lexicais explícitas, normalização de acentos e múltiplos rótulos.
- Amostra de demonstração: registros reais do dataset público, texto preservado.
- Frequências do relatório: calculadas sobre todas as 98.410 avaliações únicas.
- Limite: não é classificação semântica validada; requer conjunto-ouro e revisão humana.
- Repositório: https://github.com/vitor-souza-ime/olist-agent
