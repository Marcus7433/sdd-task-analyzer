# Relatório de Governança — Fase 3

**Status:** rascunho; a validação Docker precisa ser repetida em ambiente com Docker instalado.

## 1. Análise de alucinações

### Prompts e controles usados

Na implementação da Fase 2, os prompts pediram que o TaskAnalyzer seguisse o SDD e as `CONTEXT_RULES.md`, tivesse harness pytest e fosse integrado por Pull Request. O pedido também esclareceu que o contrato detalhado do SDD deveria prevalecer quando divergisse do texto do desafio. Na Fase 3, o pedido delimitou imagem base, diretório, comando de testes, volume Compose, estrutura de arquivos e seções do relatório.

Os controles consultados foram:

- [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md), que fixa API, validações, exceções, cálculos e formato de saída;
- [`CONTEXT_RULES.md`](CONTEXT_RULES.md), que restringe dependências funcionais, persistência, interfaces e métricas;
- [`specs/system_design_document.md`](specs/system_design_document.md), que resume componentes e aponta a especificação canônica;
- [`specs/requirements.yaml`](specs/requirements.yaml), que registra em formato estruturado a API e os comandos de validação.

Na implementação funcional, esses limites foram atendidos usando a biblioteca padrão no módulo, sem escrita de dados, UI/CLI ou métricas além do contrato. `pytest` está restrito à validação. Na infraestrutura desta fase, a dependência de teste é instalada a partir do `requirements.txt` e a execução Compose monta os arquivos em `/app` como somente leitura.

Uma divergência entre nomes do desafio e do SDD foi documentada no [PR de implementação #1](https://github.com/Marcus7433/sdd-task-analyzer/pull/1): o desafio citava `TaskValidationError` e outros nomes de métricas; o SDD aprovado define `DataInconsistenteError` e um conjunto diferente de chaves. A implementação adotou o contrato SDD para não misturar interfaces incompatíveis.

## 2. Homologação humana — Critical-in-the-Loop

O responsável humano conferiu a divergência de contrato durante a conversa de implementação e confirmou que a diferença de nomes era aceitável, mantendo o SDD como fonte funcional. O PR #1 tornou a decisão visível para revisão. Os cenários relevantes podem ser inspecionados em [`tests/test_harness.py`](tests/test_harness.py):

- **Exceção de negócio:** conclusão anterior à criação gera `DataInconsistenteError`, conforme SDD; `TaskValidationError` não foi adicionada à API.
- **Divisão por zero:** entrada vazia ou somente com tarefas pendentes resulta em médias e taxas `0.0`; coberto pelos testes de entrada vazia e tarefas pendentes.
- **Validação cronológica:** conclusão anterior à criação é erro; conclusão igual ao prazo não é atraso; conclusão posterior ao prazo é atraso. Os casos correspondentes estão cobertos pelo harness.

A revisão humana complementa os testes: o responsável escolhe qual contrato prevalece e verifica se os resultados e exceções observados fazem sentido para o requisito.

## 3. Sustentabilidade e ética

- **Rastreabilidade:** as decisões de contrato estão registradas no PR #1; o CI e sua execução podem ser consultados no [PR de CI #2](https://github.com/Marcus7433/sdd-task-analyzer/pull/2). Este relatório resume os critérios e aponta os arquivos que podem ser revisados.
- **Conformidade técnica:** a imagem solicitada é `python:3.11-slim`; o módulo usa a biblioteca padrão; o pacote `pytest` é instalado do arquivo de dependências existente. A variante `slim` limita o conteúdo da imagem em relação à imagem Python completa.
- **Reprodutibilidade:** CI e contêiner usam o mesmo arquivo de testes. O Compose monta o projeto como somente leitura para impedir que o harness modifique os arquivos locais através desse volume.
- **Confiabilidade ética:** a solução se limita aos indicadores especificados, processa entradas em memória e prevê homologação humana. Os testes demonstram os cenários cobertos; não provam ausência de todo defeito nem substituem julgamento humano.

## 4. Evidências de validação e pendências

### Harness local

Comando executado localmente em Python 3.14.3:

```text
python -m pytest tests/test_harness.py -v
16 passed, 1 warning
```

O aviso observado foi `PytestCacheWarning` ao tentar gravar no cache local do pytest no Windows. Não houve falhas. No Compose, `PYTEST_ADDOPTS=-p no:cacheprovider` evita gravação no volume somente leitura.

### Docker

Os comandos solicitados foram tentados, mas o ambiente não reconhece o comando `docker`:

```text
docker build -t task-analyzer .  — não executado: Docker CLI indisponível
docker run task-analyzer         — não executado: Docker CLI indisponível
```

Portanto, **não há confirmação de build ou de testes executados dentro do contêiner**. Rode esses comandos em uma máquina com Docker Engine/Desktop instalado antes de marcar a homologação Docker como concluída.
