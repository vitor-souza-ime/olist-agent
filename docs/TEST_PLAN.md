# Plano de testes funcionais

## Objetivo

Verificar se o protótipo executa os comportamentos centrais definidos para o Agente de Análise de Reviews na Fase 2: classificar sentimento, tema e severidade; reconhecer contradição entre nota e texto; recomendar ação; e encaminhar alegações críticas para revisão humana.

## Casos de aceitação

| ID | Entrada | Resultado esperado |
|---|---|---|
| T1 | Nota 1: “Comprei oito fronhas, mas chegaram apenas quatro.” | Tema pedido incompleto; severidade alta; conferência de separação e expedição. |
| T2 | Nota 5: “Era para chegar até 15/08, mas até hoje não recebi.” | Sentimento negativo; tema entrega; divergência nota-texto; revisão humana recomendada. |
| T3 | Nota 1: “O cartucho chegou embolorado e parece falsificado.” | Alegação crítica de autenticidade/segurança; severidade crítica; revisão humana obrigatória. |
| T4 | Nota 5: “Chegou antes do prazo e corresponde ao anunciado.” | Experiência positiva; severidade baixa; sem escalonamento. |
| T5 | Nota 3 e comentário vazio. | Informação insuficiente; sem inferência de causa; severidade indeterminada. |

## Testes automatizados complementares

- Classificação de pedido incompleto.
- Precedência do texto negativo sobre nota positiva e marcação de divergência.
- Escalonamento de alegação crítica.
- Reconhecimento de avaliação positiva.
- Tratamento de comentário vazio.
- Agregação de resumo em lote.
- Validação do esquema Olist.
- Enriquecimento por pedido sem duplicar review em pedidos com múltiplos itens.

## Critério de aprovação

Um cenário é aprovado quando tema, severidade, flags de revisão humana e divergência nota-texto correspondem aos resultados esperados. Os testes usam casos sintéticos controlados e não medem acurácia estatística sobre a população Olist.
