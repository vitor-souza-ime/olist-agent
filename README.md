# Olist Intelligent Reviews — Tech Challenge Fase 3

Agente demonstrativo de triagem de avaliações baseado no Brazilian E-Commerce Public Dataset by Olist.

## Executar localmente
```bash
pip install -r requirements.txt
python app.py
```
Abra a aba “Demonstração com avaliações reais” e clique em “Executar demonstração”. A segunda aba permite enviar outro CSV.

## Análise real
Consulte [docs/REAL_DATA_ANALYSIS.md](docs/REAL_DATA_ANALYSIS.md). A análise deduplicou 99.224 linhas por review_id, resultando em 98.410 avaliações únicas. Entre as avaliações negativas com texto, os padrões mais frequentes foram entrega/logística (5.499), qualidade/defeito (1.041) e pedido incompleto/item ausente (518).

A classificação é lexical, multi-rótulo e explicável; não deve ser confundida com interpretação semântica validada. Uma avaliação pode aparecer em mais de uma categoria. Não use os resultados para penalizar sellers ou executar reembolsos sem revisão humana.

Fonte: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
