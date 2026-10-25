# System Design Document — SDD TaskAnalyzer

## Propósito e fonte normativa

Este documento resume a arquitetura do TaskAnalyzer para orientar a leitura da solução. O contrato funcional normativo e detalhado permanece em [`task_analyzer_spec.md`](task_analyzer_spec.md); em caso de divergência, essa especificação é a fonte de verdade aprovada para este projeto.

## Arquitetura

O sistema é um módulo Python sem interface de usuário, API web, banco de dados ou persistência em arquivos. A função pública `analisar_tarefas(tarefas: list[Task]) -> dict` recebe objetos `Task` em memória e retorna os indicadores previstos no SDD.

O processamento valida cada tarefa, separa as concluídas das pendentes e calcula o tempo de conclusão e a taxa de atraso no conjunto geral e por prioridade. As prioridades `Baixa`, `Média` e `Alta` permanecem presentes no retorno mesmo quando seus indicadores são zero.

## Componentes

- `src/task_analyzer.py`: modelo `Task`, exceção `DataInconsistenteError`, validação, logging e cálculo dos indicadores.
- `tests/test_harness.py`: valida o contrato funcional com pytest.
- `.github/workflows/ci.yml`: executa o harness em push e pull request para `main` e `develop`, com Python 3.11.
- `Dockerfile` e `docker-compose.yml`: executam o harness em contêiner a partir dos arquivos do projeto.

## Restrições de implementação

O módulo funcional usa somente a biblioteca padrão Python, opera em memória e não expõe métricas fora do contrato. `pytest` é dependência apenas para validação. As regras completas estão em [`../CONTEXT_RULES.md`](../CONTEXT_RULES.md).
