# Olist Intelligent Reviews — especificação da versão com dados reais

## Objetivo

Transformar avaliações de clientes em sinais estruturados para Qualidade, Customer Service, Produto, Gestão de Sellers e gestores da experiência. O agente classifica temas e severidade, agrupa causas e recomenda ações, conforme o desenho operacional da Fase 2.

## Fluxo

1. Receber ZIP do dataset Olist.
2. Carregar reviews, orders, order_items, products e sellers.
3. Validar o esquema e deduplicar por review_id, mantendo a primeira ocorrência.
4. Normalizar o texto e executar triagem lexical multirrótulo.
5. Relacionar reviews a Orders por order_id e itens a produtos/sellers.
6. Calcular indicadores e responder a perguntas gerenciais com frequências e denominadores.
7. Analisar uma avaliação individual com evidência literal, tema, sentimento, severidade, leitura contextual e recomendação.
8. Encaminhar casos críticos e ambíguos para revisão humana.

## Camadas

- Quantitativa/lexical: padrões explícitos, reproduzíveis e sem chamada externa.
- Contextual: interpretação explicável do conjunto de sinais de uma avaliação; hipótese, não confirmação de causa.
- Semântica generativa: extensão opcional via OpenRouter para segunda opinião individual, mediante API key.
- Humana: validação de alegações críticas, ambiguidades e casos sem correspondência lexical.

## Saídas

- painel executivo;
- grupos e temas lexicais;
- associação entre prazo de entrega e nota;
- categorias com maior volume de notas baixas;
- resposta à pergunta do gestor;
- análise individual e recomendação;
- trilha de evidência e CSV.

## Limites

O agente não confirma fraude, falsificação, defeito ou culpa de seller; não autoriza reembolso, cancelamento ou penalidade. A severidade é uma triagem operacional, não uma probabilidade calibrada. A aplicação não se conecta a sistemas transacionais da Olist.
