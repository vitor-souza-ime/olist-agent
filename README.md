# Olist Intelligent Reviews — Tech Challenge Fase 3

Protótipo funcional do Agente de Análise de Reviews, evoluído a partir do desenho operacional da Fase 2 e executado sobre o dataset público real da Olist.

> Projeto acadêmico independente, sem vínculo oficial com a Olist. Não executa ações em sistemas de produção e não substitui revisão humana.

## Resultados reais da execução

- 99.224 linhas originais em Order_Reviews.
- 98.410 review_id únicos após remover 814 linhas excedentes por identificador repetido.
- Nota média: 4,09/5.
- 14.396 avaliações (14,6%) receberam nota 1 ou 2.
- 10.861 avaliações com nota 1 ou 2 possuem comentário textual.
- A triagem lexical encontrou pelo menos um padrão em 5.719 comentários (52,7% dos comentários negativos com texto).

Três grupos prioritários:

| Grupo | Comentários | Percentual |
|---|---:|---:|
| Entrega e cumprimento do pedido | 3.970 | 36,6% |
| Produto: qualidade, defeito ou divergência | 1.255 | 11,6% |
| Pós-venda: atendimento, devolução e pagamento | 852 | 7,8% |

Os grupos são multirrótulo e se sobrepõem; os percentuais não são aditivos. A triagem lexical identifica menções explícitas e não equivale a uma classificação semântica validada por especialistas.

## Aplicação

O arquivo `app.py` inicia a versão com dados reais:

```bash
python -m pip install -r requirements.txt
python app.py
```

No Windows, também é possível executar `INSTALAR_E_INICIAR.bat`. Abra `http://127.0.0.1:7860`.

A interface oferece:
- Painel executivo com métricas reais;
- pergunta gerencial respondida a partir dos indicadores calculados;
- análise individual de reviews reais;
- evidências literais, leitura contextual, severidade e recomendação;
- carregamento do ZIP original do dataset.

## Dados

Baixe o dataset oficial: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Salve o ZIP em `data/olist_public_dataset.zip` ou carregue-o pela interface. O ZIP bruto não é versionado neste repositório por tamanho e para evitar redistribuição desnecessária.

O agente lê reviews, orders, order_items, products e sellers. A unidade de análise é review_id único; linhas excedentes de IDs repetidos são removidas mantendo a primeira ocorrência. Itens de um pedido são agregados antes do relacionamento, evitando multiplicar avaliações.

Fonte: Olist, *Brazilian E-Commerce Public Dataset by Olist*, Kaggle (2018). Licença indicada na fonte: CC BY-NC-SA 4.0. Atribuição, uso não comercial e compartilhamento pela mesma licença devem ser respeitados.

## Demonstração em terminal

```bash
python run_demo.py
```

O script carrega o dataset real, responde à pergunta do gestor e analisa uma avaliação real de pedido incompleto.

## Testes

```bash
python -m pytest -q
```

A versão local foi validada com 16 testes automatizados aprovados.

## Separação metodológica

1. Quantitativa/lexical: contagem reproduzível de padrões explícitos em reviews com nota 1 ou 2 e texto.
2. Contextual: interpretação explicável de uma avaliação individual; hipótese operacional, não confirmação da causa.
3. Semântica generativa: extensão opcional via OpenRouter para uma segunda opinião individual; requer API key e não calcula as frequências do relatório.
4. Revisão humana: alegações críticas, ambiguidades, divergência nota-texto e comentários sem correspondência lexical.

## Documentação e auditoria

- `docs/DATA_ANALYSIS_REAL.md`: filtros, denominadores, métricas e limitações;
- `docs/AGENT_REAL.md`: especificação do agente;
- `docs/DEMO_SCRIPT.md`: roteiro de demonstração de até cinco minutos;
- `data/analysis_snapshot.json`: agregados calculados;
- `data/dataset_manifest.json`: origem, SHA-256 e tabelas analisadas.

## Repositório

https://github.com/vitor-souza-ime/olist-agent
