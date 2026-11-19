# Olist Intelligent Reviews — Tech Challenge Fase 3

Protótipo funcional do Agente de Análise de Reviews, como evolução do Olist Intelligent Marketplace definido nas Fases 1 e 2. A aplicação permite carregar o dataset público da Olist, consultar um painel executivo, perguntar ao agente, analisar avaliações reais individualmente e consultar os critérios de auditoria e revisão humana.

## Executar localmente

```bash
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:7860` e carregue o ZIP do dataset Olist. O arquivo integral não é versionado neste repositório; baixe-o em https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

## Evidências da análise integral

A execução registrada em 19/11/2026 utilizou 99.224 linhas de avaliações, resultando em 98.410 `review_id` únicos após a remoção de 814 linhas excedentes. A nota média foi 4,09/5; 14.396 avaliações (14,6%) receberam notas 1 ou 2; 10.861 dessas avaliações possuíam comentário textual.

A triagem lexical identificou padrões em 5.719 comentários (52,7% dos comentários de notas 1–2 com texto). Os três grupos prioritários foram:

| Grupo | Comentários | Percentual |
|---|---:|---:|
| Entrega e cumprimento do pedido | 3.970 | 36,6% |
| Produto: qualidade, defeito ou divergência | 1.255 | 11,6% |
| Pós-venda: atendimento, devolução e pagamento | 852 | 7,8% |

Os grupos são multirrótulo: uma avaliação pode aparecer em mais de um grupo e os percentuais não são aditivos. A triagem lexical é uma contagem reproduzível de padrões explícitos, não uma classificação semântica validada por especialistas. A segunda opinião via OpenRouter é opcional, exige API key e não foi usada para calcular as métricas.

## Interface e fluxo do agente

- Painel executivo: indicadores, problemas prioritários, categorias e contexto de entrega.
- Pergunte ao agente: respostas gerenciais construídas a partir dos indicadores calculados.
- Analisar avaliação real: comentário original, tema, severidade, evidência e recomendação.
- Metodologia e auditoria: regras, limites, rastreabilidade e critérios de revisão humana.

## Testes e auditoria

Comando: `python -m pytest -q` — 17 testes automatizados aprovados na versão local documentada.

- [Análise real do dataset](docs/REAL_DATA_ANALYSIS.md)
- [Análise de dados](docs/DATA_ANALYSIS_REAL.md)
- [Resultados dos testes](docs/TEST_RESULTS.md)
- [Plano de testes](docs/TEST_PLAN.md)
- [Trilha de auditoria](docs/AUDIT_TRAIL.md)
- [Roteiro de demonstração](docs/DEMO_SCRIPT.md)

## Limites e governança

O agente prioriza e recomenda; não executa reembolsos, cancelamentos ou penalidades. Alegações de fraude, autenticidade, segurança ou discriminação, divergências entre nota e texto e comentários ambíguos exigem validação humana. As métricas descrevem o dataset histórico e não representam a operação atual da Olist.

Fonte: Olist. *Brazilian E-Commerce Public Dataset by Olist*. Kaggle, 2018. Licença indicada na fonte: CC BY-NC-SA 4.0. Respeite atribuição e condições de uso.

Repositório: https://github.com/vitor-souza-ime/olist-agent
