# Análise real — Brazilian E-Commerce Public Dataset by Olist

Fonte: Olist, *Brazilian E-Commerce Public Dataset by Olist*, Kaggle (2018): https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce.

## Preparação

- Linhas originais em Order_Reviews: 99.224.
- Linhas excedentes por review_id repetido removidas: 814.
- Avaliações únicas analisadas: 98.410.
- Nota média: 4,09/5.
- Notas 1 ou 2: 14.396 (14,6%).
- Avaliações com texto: 42.370; sem texto: 56.040.
- Entre as avaliações com nota 1 ou 2, 10.861 possuem comentário textual.

## Triagem lexical em avaliações negativas com texto

| Grupo multirrótulo | Contagem | % das negativas com texto |
|---|---:|---:|
| Entrega e cumprimento do pedido | 3.970 | 36,6% |
| Produto: qualidade, defeito ou divergência | 1.255 | 11,6% |
| Pós-venda: atendimento, devolução e pagamento | 852 | 7,8% |
| Embalagem e acondicionamento | 194 | 1,8% |
| Autenticidade, fraude ou segurança | 83 | 0,8% |

Ao menos um padrão lexical foi identificado em 5.719 comentários (52,7%). Outros 5.142 (47,3%) não acionaram os padrões definidos e não foram forçados a uma categoria.

Os grupos são multirrótulo: uma avaliação pode aparecer em mais de um grupo e os percentuais não são aditivos. As contagens representam triagem lexical reproduzível, não interpretação semântica validada por especialistas.

## Limites

A triagem pode falhar diante de ironia, ambiguidade, negação complexa, erros ortográficos e vocabulário não coberto. Recomenda-se construir um conjunto-ouro anotado por especialistas e avaliar precisão, recall e F1 por tema antes do uso operacional. A análise completa, incluindo temas individuais, relação entre atraso e avaliação, categorias e denominadores, está em [DATA_ANALYSIS_REAL.md](DATA_ANALYSIS_REAL.md).
