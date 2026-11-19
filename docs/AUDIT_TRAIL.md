# Trilha de auditoria — Olist Intelligent Reviews

- Projeto: Olist Intelligent Marketplace — Tech Challenge Fase 3.
- Fonte: Brazilian E-Commerce Public Dataset by Olist (Kaggle, 2018).
- Arquivo analisado: ZIP original fornecido pelo usuário em 19/11/2026.
- Linhas brutas de Order_Reviews: 99.224; duplicatas por review_id: 814; avaliações únicas: 98.410.
- Deduplicação: manter a primeira ocorrência de cada review_id.
- Triagem: regras lexicais explícitas, normalização de acentos e classificação multirrótulo.
- Denominador da triagem: 10.861 avaliações com nota 1 ou 2 e comentário textual.
- Padrões lexicais encontrados: 5.719 (52,7%). Os demais não foram forçados para categorias.
- Grupos: entrega/cumprimento 3.970; produto/qualidade/divergência 1.255; pós-venda 852.
- Testes automatizados: 17 aprovados na versão local documentada.
- Limite: não é classificação semântica validada; requer conjunto-ouro e revisão humana.
- A segunda opinião OpenRouter não foi executada e não foi usada nas métricas.
- O protótipo não executa reembolsos, cancelamentos, sanções ou alterações de dados transacionais.
- Repositório: https://github.com/vitor-souza-ime/olist-agent
