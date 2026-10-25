# Relatório de Governança — Fase 3

**Status:** rascunho. A validação Docker precisa ser repetida em ambiente com Docker instalado.

## 1. Análise de alucinações

### Prompts e controles usados

**Registro resumido da conversa desta implementação:** na Fase 2, os prompts pediram que o TaskAnalyzer seguisse o SDD e as `CONTEXT_RULES.md`, tivesse harness pytest e fosse integrado por Pull Request. Também foi esclarecido que o contrato detalhado do SDD deveria prevalecer quando divergisse do texto do desafio. Na Fase 3, o pedido delimitou imagem base, diretório, comando de testes, volume Compose, estrutura de arquivos e seções do relatório. Este resumo não é uma transcrição integral nem um registro versionado dos prompts.

Os controles consultados no repositório foram:

- [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md), que fixa API, validações, exceções, cálculos e formato de saída;
- [`CONTEXT_RULES.md`](CONTEXT_RULES.md), que restringe dependências funcionais, persistência, interfaces e métricas;
- [`specs/system_design_document.md`](specs/system_design_document.md), que resume componentes e aponta a especificação canônica;
- [`specs/requirements.yaml`](specs/requirements.yaml), que registra requisitos funcionais e de execução em formato estruturado.

A implementação funcional usa a biblioteca padrão no módulo, sem escrita de dados, interface de usuário ou métricas além do contrato. `pytest` é usado para validação. Na infraestrutura desta fase, as dependências são instaladas a partir de `requirements.txt` e o Compose monta os arquivos em `/app` como somente leitura.

Uma divergência entre nomes do desafio e do SDD foi registrada no [PR de implementação #1](https://github.com/Marcus7433/sdd-task-analyzer/pull/1): o desafio citava `TaskValidationError` e nomes diferentes para métricas; o SDD define `DataInconsistenteError` e outro conjunto de chaves. A implementação segue o contrato SDD.

## 2. Homologação humana — Critical-in-the-Loop

Segundo o registro da conversa de implementação, o responsável humano conferiu a divergência de contrato e confirmou que a diferença de nomes era aceitável, mantendo o SDD como fonte funcional. O [PR #1](https://github.com/Marcus7433/sdd-task-analyzer/pull/1) é a referência de revisão disponível no repositório; a conversa integral não está versionada como evidência.

Os cenários correspondentes podem ser inspecionados em [`tests/test_harness.py`](tests/test_harness.py):

- **Exceção de negócio:** conclusão anterior à criação gera `DataInconsistenteError`, conforme o SDD; `TaskValidationError` não foi adicionada à API.
- **Divisão por zero:** entrada vazia ou somente com tarefas pendentes resulta em médias e taxas `0.0`; os casos são cobertos pelo harness.
- **Validação cronológica:** conclusão anterior à criação é erro; conclusão igual ao prazo não é atraso; conclusão posterior ao prazo é atraso. Os casos estão cobertos pelo harness.

A revisão humana complementa os testes ao decidir qual contrato prevalece e conferir se os resultados observados atendem ao requisito.

## 3. Sustentabilidade e ética

- **Rastreabilidade:** as decisões de contrato estão registradas no PR #1. O workflow de CI e sua revisão podem ser consultados no [PR de CI #2](https://github.com/Marcus7433/sdd-task-analyzer/pull/2). O estado atual dos checks remotos não foi consultado para este relatório.
- **Conformidade técnica:** a imagem configurada é `python:3.11-slim`; o módulo funcional usa a biblioteca padrão; a dependência de teste é instalada a partir do arquivo de dependências do projeto.
- **Reprodutibilidade:** CI e contêiner usam o mesmo arquivo de testes. O Compose monta o projeto como somente leitura para impedir que o harness altere os arquivos locais através desse volume.
- **Confiabilidade ética:** a solução se limita aos indicadores especificados, processa entradas em memória e prevê homologação humana. Os testes demonstram os cenários cobertos; não provam ausência de todo defeito nem substituem julgamento humano.

## 4. Evidências de validação e pendências

### Harness local

Execução observada nesta sessão em Python 3.14.3; não há log local versionado:

```text
python -m pytest tests/test_harness.py -v
16 passed, 1 warning
```

O aviso observado foi `PytestCacheWarning` ao tentar gravar no cache local do pytest no Windows. Não houve falhas nessa execução. O [PR de CI #2](https://github.com/Marcus7433/sdd-task-analyzer/pull/2) permite revisar o workflow; seu estado de checks não foi verificado durante a preparação deste relatório. No Compose, `PYTEST_ADDOPTS=-p no:cacheprovider` evita gravação no volume somente leitura.

### Docker

Os comandos solicitados foram tentados, mas o ambiente não reconhece o comando `docker`:

```text
docker build -t task-analyzer .  — não executado: Docker CLI indisponível
docker run task-analyzer         — não executado: Docker CLI indisponível
```

Portanto, não há confirmação de build ou de testes executados dentro do contêiner. Rode esses comandos em uma máquina com Docker Engine/Desktop instalado antes de marcar a homologação Docker como concluída.
