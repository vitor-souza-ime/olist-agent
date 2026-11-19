# Resultados da validação funcional

Data da execução: 19/11/2026.

## Testes automatizados

Execução: python -m pytest -q

Resultado: 11 passed.

## Cenários de aceitação exibidos na aplicação

| ID | Resultado | Evidência principal |
|---|---|---|
| T1 — Pedido incompleto | APROVADO | Tema “Pedido incompleto / item ausente”; severidade alta. |
| T2 — Nota e texto divergentes | APROVADO | Tema “Entrega e logística”; texto negativo apesar da nota 5; divergência identificada; revisão humana recomendada. |
| T3 — Alegação crítica | APROVADO | Tema crítico; severidade crítica; revisão humana obrigatória. |
| T4 — Experiência positiva | APROVADO | Tema positivo; severidade baixa; sem escalonamento. |
| T5 — Comentário ausente | APROVADO | Informação insuficiente; causa não inferida. |

Resultado: 5/5 cenários aprovados.

## Teste de inicialização da interface

A interface Gradio foi iniciada localmente e respondeu com HTTP 200 em http://127.0.0.1:7860/.

## O que não foi validado

- Não foi executado um processamento do arquivo completo do Kaggle nesta sessão, pois o CSV integral e a amostra anterior de 100 registros não estavam disponíveis como arquivos recuperáveis.
- Não foi realizada chamada ao OpenRouter, pois não foi fornecida API key.
- Não foram medidos ganhos de produtividade, redução de tempo, CSAT ou impacto financeiro em operação real.

## Interpretação

Os resultados demonstram o funcionamento do fluxo e dos controles definidos para os cinco cenários. Não representam uma avaliação de acurácia generalizável, validação em produção ou comprovação de impacto financeiro.
