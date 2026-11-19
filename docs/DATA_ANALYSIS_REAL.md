# Análise quantitativa do dataset real da Olist

## Fonte e integridade

Fonte: Olist, *Brazilian E-Commerce Public Dataset by Olist* (Kaggle, 2018): https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

Arquivo recebido nesta entrega: archive.zip. SHA-256: 967e41e04fc306fe604e2a693f488995a8b41e5047418f8a5c8e4abd6deca784.

O ZIP contém nove tabelas. O agente usa reviews, orders, order_items, products e sellers; não precisa carregar customers, geolocation ou payments para a triagem inicial.

## Preparação e qualidade

| Indicador | Resultado |
|---|---:|
| Linhas originais em Order_Reviews | 99.224 |
| review_id únicos | 98.410 |
| Linhas excedentes por review_id repetido | 814 |
| Reviews analisados após deduplicação | 98.410 |
| Nota média | 4,09/5 |
| Reviews com comentário textual | 42.370 |
| Reviews sem comentário textual | 56.040 |
| Reviews com nota 1 ou 2 | 14.396 (14,6%) |
| Notas 1 ou 2 com comentário textual | 10.861 |
| Notas 1 ou 2 sem comentário textual | 3.535 |

A unidade de análise é review_id único. Para IDs repetidos, mantém-se a primeira ocorrência na ordem do arquivo. A regra evita contagem duplicada da mesma chave e está registrada no manifesto.

## Distribuição das notas

| Nota | Quantidade | Percentual |
|---:|---:|---:|
| 1 | 11.282 | 11,5% |
| 2 | 3.114 | 3,2% |
| 3 | 8.097 | 8,2% |
| 4 | 19.007 | 19,3% |
| 5 | 56.910 | 57,8% |

## Triagem lexical — grupos de problemas

Os padrões são aplicados ao texto normalizado. A triagem foi limitada aos 10.861 comentários com nota 1 ou 2 e texto. Uma avaliação pode pertencer a mais de um grupo.

| Grupo | Comentários com sinal | Percentual |
|---|---:|---:|
| Entrega e cumprimento do pedido | 3.970 | 36,6% |
| Produto: qualidade, defeito ou divergência | 1.255 | 11,6% |
| Pós-venda: atendimento, devolução e pagamento | 852 | 7,8% |
| Embalagem e acondicionamento | 194 | 1,8% |
| Autenticidade, fraude ou segurança | 83 | 0,8% |

Os grupos se sobrepõem; os percentuais não são aditivos. Ao menos um padrão lexical foi encontrado em 5.719 comentários (52,7%). Outros 5.142 (47,3%) não acionaram os padrões definidos. Isso não significa ausência de problema: esses comentários precisam de leitura semântica complementar ou revisão humana.

### Temas individuais

| Tema | Contagem | Percentual |
|---|---:|---:|
| Entrega e logística | 3.206 | 29,5% |
| Qualidade ou defeito do produto | 892 | 8,2% |
| Pedido incompleto / item ausente | 840 | 7,7% |
| Devolução, estorno e pagamento | 620 | 5,7% |
| Produto divergente do anúncio | 387 | 3,6% |
| Atendimento e comunicação | 259 | 2,4% |
| Embalagem e acondicionamento | 194 | 1,8% |
| Autenticidade, fraude ou segurança | 83 | 0,8% |

## Relação entre prazo de entrega e avaliação

Atraso foi definido como order_delivered_customer_date posterior a order_estimated_delivery_date.

| Situação | Reviews | Nota média | Notas 1–2 |
|---|---:|---:|---:|
| Entregue após a estimativa | 7.633 | 2,57 | 54,1% |
| No prazo/antecipado | 87.974 | 4,30 | 9,2% |
| Sem data de entrega | 2.803 | 1,74 | 78,2% |

Entre os pedidos com data de entrega disponível, 8,0% chegaram após a estimativa. O atraso médio foi 9,45 dias e a mediana, 5,78 dias. A associação é observacional e não prova causalidade exclusiva. Reviews sem data de entrega são mantidos em grupo separado.

## Categorias com maior volume de avaliações baixas

| Categoria | Associações review-categoria | Notas 1–2 | Taxa de notas 1–2 |
|---|---:|---:|---:|
| Cama, mesa e banho | 9.273 | 1.547 | 16,7% |
| Beleza e saúde | 8.752 | 1.110 | 12,7% |
| Móveis e decoração | 6.368 | 1.056 | 16,6% |
| Informática e acessórios | 6.626 | 1.056 | 15,9% |
| Esporte e lazer | 7.642 | 990 | 13,0% |

Pedidos com mais de uma categoria aparecem em cada associação correspondente. Portanto, as contagens por categoria não são avaliações únicas nem aditivas.

## Exemplos reais para demonstração

- review_id 96ab47052a57bbfbba3b48d4203cf1f3, nota 1: o cliente relata ter recebido metade do pedido embora a nota fiscal indique toda a mercadoria. Leitura: possível divergência entre faturamento, separação e recebimento.
- review_id cd76397f23913425751779c775bb8499, nota 1: o cliente relata não recebimento após mais de um mês e questiona o destino do dinheiro. Leitura: problema logístico associado à resolução financeira.
- review_id 8ccb6f10802a0a4341f9a339cdc7f715, nota 1: o cliente relata que uma panela vaza durante o cozimento. Leitura: possível falha funcional; não confirma defeito técnico.

## Recomendações

1. Entrega: priorizar rastreamento, comprovante, conferência de itens e comunicação proativa.
2. Produto: cruzar defeitos e divergências com SKU, anúncio, imagens, lote e fornecedor.
3. Pós-venda: revisar tickets sem retorno, cancelamentos, devoluções e estornos.

## Limitações

A triagem lexical é reproduzível, mas não identifica necessariamente ironia, paráfrases, erros ortográficos ou negação complexa. As contagens não são acurácia de modelo nem rótulos semânticos validados. Uma amostra estratificada deve ser rotulada por especialistas para medir precisão e recall por tema.
