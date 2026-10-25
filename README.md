# SDD TaskAnalyzer

[![CI](https://github.com/Marcus7433/sdd-task-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/Marcus7433/sdd-task-analyzer/actions/workflows/ci.yml)

Módulo Python em memória para calcular indicadores de conclusão e atraso de tarefas. O contrato funcional canônico está em [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md), e as restrições para o código funcional estão em [`CONTEXT_RULES.md`](CONTEXT_RULES.md).

## Contrato público

A função principal é `analisar_tarefas(tarefas: list[Task]) -> dict`. Ela calcula tempo médio de conclusão em horas e taxa de atraso geral e por prioridade. O retorno contém somente as chaves definidas no SDD.

## Requisitos

- Python 3.11 ou superior.
- Docker Engine e Docker Compose v2 para execução em contêiner.
- pytest para executar o Test Harness.

## Executar localmente

Instale as dependências e execute o harness:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests/test_harness.py -v
```

O TaskAnalyzer é uma biblioteca, sem interface CLI. Para chamar o analisador no interpretador Python:

```powershell
$env:PYTHONPATH = "src"
python
```

```python
from datetime import datetime
from task_analyzer import Task, analisar_tarefas

tarefa = Task(
    id="1",
    titulo="Exemplo",
    prioridade="Alta",
    status="Concluída",
    data_criacao=datetime(2024, 1, 1, 8),
    data_limite=datetime(2024, 1, 2, 8),
    data_conclusao=datetime(2024, 1, 2, 10),
)
analisar_tarefas([tarefa])
```

## Executar com Docker

Construa a imagem e execute os testes configurados como comando padrão:

```powershell
docker build -t task-analyzer .
docker run task-analyzer
```

## Executar com Docker Compose

O serviço `test-runner` monta o diretório do projeto como somente leitura em `/app`:

```powershell
docker compose run test-runner
```

## Integração contínua

O GitHub Actions executa o harness em `push` e `pull_request` direcionados a `main` e `develop`, usando Ubuntu e Python 3.11. O badge no topo mostra o estado reportado pelo workflow `CI`.

## Arquivos de especificação

- [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md): contrato funcional SDD detalhado e canônico.
- [`specs/system_design_document.md`](specs/system_design_document.md): visão resumida da arquitetura, subordinada ao contrato canônico.
- [`specs/requirements.yaml`](specs/requirements.yaml): resumo estruturado dos requisitos funcionais e de execução.
