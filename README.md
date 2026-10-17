# SDD TaskAnalyzer

Módulo Python em memória para calcular indicadores de conclusão e atraso de tarefas, conforme o contrato técnico em [specs/task_analyzer_spec.md](specs/task_analyzer_spec.md).

## Contrato público

A função principal é `analisar_tarefas(tarefas: list[Task]) -> dict`. Ela calcula tempo médio de conclusão em horas e taxa de atraso geral e por prioridade. O retorno contém somente as chaves definidas no SDD.

O contrato funcional da especificação SDD prevalece para a assinatura pública e para a estrutura da saída. As diferenças entre esses requisitos e os exemplos de nomes/métricas do desafio serão registradas na revisão do PR.

## Requisitos

- Python 3.11 ou superior.
- pytest para executar o Test Harness.

## Executar os testes

Instale a dependência de teste e rode a suíte:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
```

Os testes ficam em `tests/test_harness.py`. O módulo em `src/task_analyzer.py` usa apenas a biblioteca padrão do Python.
'

## Estado

Em desenvolvimento.
