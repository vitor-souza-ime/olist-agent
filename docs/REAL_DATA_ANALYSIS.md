# Análise real — Brazilian E-Commerce Public Dataset by Olist

Fonte: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Preparação
- Linhas originais em order_reviews: 99.224.
- Linhas repetidas por review_id removidas: 814.
- Avaliações únicas analisadas: 98.410.
- Nota média: 4,089/5.
- Notas 1 ou 2: 14.396.
- Avaliações com texto: 42.370.
- Avaliações sem título e sem comentário: 56.040.
- Das avaliações negativas, 10.861 têm texto.

## Triagem lexical em negativas com texto
| Tema | Contagem | % das negativas com texto |
|---|---:|---:|
| Entrega e logística | 5.499 | 50,63% |
| Qualidade / defeito do produto | 1.041 | 9,58% |
| Pedido incompleto / item ausente | 518 | 4,77% |
| Produto divergente do anúncio | 308 | 2,84% |
| Pagamento / estorno | 349 | 3,21% |
| Embalagem | 243 | 2,24% |
| Atendimento / comunicação | 209 | 1,92% |

Categorias multi-rótulo; percentuais não somam 100%. Contagens são padrões lexicais, não interpretação semântica validada.

## Limites
A triagem lexical pode errar por contexto, ironia, negação, erros ortográficos e vocabulário não coberto. Recomenda-se conjunto-ouro anotado por especialistas e avaliação de precisão, recall e F1 antes do uso operacional.
