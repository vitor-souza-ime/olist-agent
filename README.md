# Olist Intelligent Reviews

Protótipo funcional do Agente de Análise de Reviews, desenvolvido como evolução do Tech Challenge — Fase 2 para a Fase 3 (Experiment & Build).

> Protótipo acadêmico independente, sem vínculo oficial com a Olist. Não executa ações em sistemas de produção e não substitui a revisão humana.

## Entregáveis

- [Interface da aplicação](app.py)
- [Motor de classificação](olist_agent/engine.py)
- [Leitura e enriquecimento de dados](olist_agent/data.py)
- [Integração opcional com OpenRouter](olist_agent/llm.py)
- [Testes automatizados](tests/)
- Código, testes e documentação de auditoria disponíveis neste repositório.

## O que a aplicação faz

- Recebe uma avaliação individual ou um lote de avaliações.
- Classifica sentimento, tema e severidade.
- Detecta possíveis divergências entre nota e comentário.
- Recomenda uma ação corretiva e uma área responsável.
- Encaminha alegações potencialmente críticas de fraude, autenticidade ou segurança para revisão humana obrigatória.
- Gera resumo executivo, frequências de causas e arquivo CSV auditável.
- Permite carregar a tabela `olist_order_reviews_dataset.csv`, arquivos CSV auxiliares ou um ZIP com o dataset Olist.
- Pode solicitar uma segunda análise a um modelo via OpenRouter, de forma opcional e manual.

## Executar localmente

Requer Python 3.10 ou superior.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:7860` no navegador.

## Testar

```bash
python -m pytest -q
python run_demo.py
```

Validação local desta entrega: 11 testes automatizados aprovados e 5/5 cenários de aceitação aprovados.

## Dados

A aplicação inicia com `data/demo_reviews.csv`, contendo dez casos sintéticos criados para demonstrar comportamentos específicos. Eles não são registros reais da Olist e não devem ser usados para inferir padrões de negócio.

Para uma análise real, obtenha o Brazilian E-Commerce Public Dataset by Olist no Kaggle e carregue `olist_order_reviews_dataset.csv`. Para enriquecer as avaliações, carregue também:

- `olist_orders_dataset.csv`;
- `olist_order_items_dataset.csv`;
- `olist_products_dataset.csv`;
- `olist_sellers_dataset.csv`.

O protótipo agrega itens por `order_id` antes do relacionamento, evitando multiplicar uma avaliação quando o pedido possui mais de um item. Os campos de cliente e geolocalização não são necessários para o escopo inicial do agente de reviews.

Dataset original: [Brazilian E-Commerce Public Dataset by Olist — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Consulte a licença e os termos de uso do dataset na fonte original antes de redistribuir dados.

## Integração opcional com OpenRouter

O motor local funciona sem API key. Para solicitar uma segunda análise generativa de uma avaliação individual:

1. Abra a aba **Analisar avaliação**.
2. Expanda **Integração generativa opcional (OpenRouter)**.
3. Informe sua chave e o identificador do modelo disponível na sua conta.
4. Execute o agente.

A chamada externa só ocorre quando o usuário fornece a chave e executa a análise. A chave não está incluída no repositório. Não envie dados pessoais ou informações confidenciais. A saída da LLM é uma segunda opinião e deve ser comparada com a evidência e a revisão humana.

## Arquitetura resumida

```text
CSV/ZIP Olist ou entrada manual
              |
              v
      Validação e contexto
              |
              v
     Motor local de triagem
   sentimento / tema / severidade
              |
              v
     Recomendação e prioridade
              |
        +-----+------+
        |            |
        v            v
  Caso comum    Alegação crítica
        |            |
        v            v
  Saída/CSV    Revisão humana
```

A integração OpenRouter é opcional e não substitui o motor local nem os controles humanos.

## Limites conhecidos

- A classificação local usa regras e palavras-chave explícitas; pode falhar com ironia, ambiguidade, negação complexa, erros ortográficos e comentários multilíngues.
- A severidade é uma triagem operacional, não uma probabilidade calibrada.
- A frequência de causas descreve somente o arquivo carregado; não deve ser generalizada para toda a Olist sem amostragem representativa.
- Não há integração com CRM, transportadoras, sistemas de pagamento ou gestão de sellers.
- O protótipo não aplica sanções, reembolsos, cancelamentos ou compensações.
- A integração com LLM não foi executada na validação local porque não foi fornecida uma API key.
- A amostra de 100 avaliações mencionada em uma demonstração anterior não foi recuperada com os registros individuais e critérios de seleção auditáveis; seus resultados não são apresentados como métricas confirmadas.

## Auditoria

- [Plano de testes](docs/TEST_PLAN.md)
- [Resultados dos testes](docs/TEST_RESULTS.md)
- [Arquitetura e fluxo](docs/ARCHITECTURE.md)
- [Trilha de auditoria](docs/AUDIT_TRAIL.md)
- [Roteiro do vídeo executivo](docs/DEMO_SCRIPT.md)

## Licença

O código deste protótipo está sob MIT. Isso não altera nem substitui a licença do dataset Olist, que permanece regida pelos termos da fonte original.
