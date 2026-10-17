"""Test harness for the TaskAnalyzer SDD contract."""

from __future__ import annotations

import importlib
from importlib.util import find_spec
import logging
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))


def test_task_analyzer_module_is_available() -> None:
    """Catch a missing implementation through an assertion, not a collection error."""
    assert find_spec("task_analyzer") is not None, "task_analyzer.py has not been implemented"


@pytest.fixture
def analyzer() -> ModuleType:
    """Load the implementation, skipping dependent checks until the RED test passes."""
    if find_spec("task_analyzer") is None:
        pytest.skip("task_analyzer.py has not been implemented yet")
    return importlib.import_module("task_analyzer")


def make_task(
    task_type: type[Any],
    task_id: Any,
    title: str,
    priority: str,
    status: str,
    created: datetime | None,
    deadline: datetime | None,
    completed: datetime | None,
) -> Any:
    """Build a Task using the module's declared input model."""
    return task_type(
        id=task_id,
        titulo=title,
        prioridade=priority,
        status=status,
        data_criacao=created,
        data_limite=deadline,
        data_conclusao=completed,
    )


@pytest.fixture
def successful_tasks(analyzer: ModuleType) -> list[Any]:
    """Return the SDD's hand-calculated four-completion example."""
    task_type = analyzer.Task
    return [
        make_task(
            task_type,
            "1",
            "Implementar tela de login",
            "Alta",
            "Concluída",
            datetime(2024, 1, 1, 8),
            datetime(2024, 1, 2, 18),
            datetime(2024, 1, 2, 12),
        ),
        make_task(
            task_type,
            "2",
            "Corrigir bug do relatório financeiro",
            "Média",
            "Concluída",
            datetime(2024, 1, 1, 10),
            datetime(2024, 1, 3, 10),
            datetime(2024, 1, 4, 10),
        ),
        make_task(
            task_type,
            "3",
            "Atualizar documentação da API",
            "Baixa",
            "Concluída",
            datetime(2024, 1, 2, 14),
            datetime(2024, 1, 5, 14),
            datetime(2024, 1, 4, 14),
        ),
        make_task(
            task_type,
            "4",
            "Refatorar módulo de pagamentos",
            "Alta",
            "Concluída",
            datetime(2024, 1, 3, 9),
            datetime(2024, 1, 5, 9),
            datetime(2024, 1, 5, 15),
        ),
        make_task(
            task_type,
            "5",
            "Criar testes de integração",
            "Média",
            "Pendente",
            datetime(2024, 1, 4, 8),
            datetime(2024, 1, 10, 18),
            None,
        ),
        make_task(
            task_type,
            "6",
            "Revisar pull requests abertos",
            "Baixa",
            "Pendente",
            datetime(2024, 1, 5, 11),
            datetime(2024, 1, 8, 11),
            None,
        ),
    ]


def test_analisar_tarefas_returns_exact_sdd_metrics(
    analyzer: ModuleType, successful_tasks: list[Any]
) -> None:
    """Catch wrong filters, hour units, delay rates, or output schema."""
    result = analyzer.analisar_tarefas(successful_tasks)

    assert set(result) == {
        "total_tarefas_concluidas",
        "tempo_medio_conclusao_geral",
        "taxa_atraso_geral",
        "indicadores_por_prioridade",
    }
    assert result == {
        "total_tarefas_concluidas": 4,
        "tempo_medio_conclusao_geral": 50.5,
        "taxa_atraso_geral": 50.0,
        "indicadores_por_prioridade": {
            "Baixa": {
                "total_tarefas_concluidas": 1,
                "tempo_medio_conclusao": 48.0,
                "taxa_atraso": 0.0,
            },
            "Média": {
                "total_tarefas_concluidas": 1,
                "tempo_medio_conclusao": 72.0,
                "taxa_atraso": 100.0,
            },
            "Alta": {
                "total_tarefas_concluidas": 2,
                "tempo_medio_conclusao": 41.0,
                "taxa_atraso": 50.0,
            },
        },
    }


def test_empty_input_returns_zero_metrics_for_all_priorities(
    analyzer: ModuleType,
) -> None:
    """Catch divisions by zero and missing fixed priority groups."""
    assert analyzer.analisar_tarefas([]) == {
        "total_tarefas_concluidas": 0,
        "tempo_medio_conclusao_geral": 0.0,
        "taxa_atraso_geral": 0.0,
        "indicadores_por_prioridade": {
            "Baixa": {
                "total_tarefas_concluidas": 0,
                "tempo_medio_conclusao": 0.0,
                "taxa_atraso": 0.0,
            },
            "Média": {
                "total_tarefas_concluidas": 0,
                "tempo_medio_conclusao": 0.0,
                "taxa_atraso": 0.0,
            },
            "Alta": {
                "total_tarefas_concluidas": 0,
                "tempo_medio_conclusao": 0.0,
                "taxa_atraso": 0.0,
            },
        },
    }


def test_pending_tasks_are_ignored_and_logged(
    analyzer: ModuleType, caplog: pytest.LogCaptureFixture
) -> None:
    """Catch pending tasks leaking into metrics or skipping required logs."""
    task_type = analyzer.Task
    pending_tasks = [
        make_task(task_type, "10", "Pendente A", "Alta", "Pendente", None, None, None),
        make_task(task_type, "11", "Pendente B", "Baixa", "Pendente", None, None, None),
    ]

    with caplog.at_level(logging.INFO, logger=analyzer.__name__):
        result = analyzer.analisar_tarefas(pending_tasks)

    assert result["total_tarefas_concluidas"] == 0
    assert result["tempo_medio_conclusao_geral"] == 0.0
    assert result["taxa_atraso_geral"] == 0.0
    assert [entry.message for entry in caplog.records if entry.levelno == logging.WARNING] == [
        "Tarefa ID 10 ignorada (status=Pendente).",
        "Tarefa ID 11 ignorada (status=Pendente).",
        "Nenhuma tarefa concluída com prioridade Baixa.",
        "Nenhuma tarefa concluída com prioridade Média.",
        "Nenhuma tarefa concluída com prioridade Alta.",
    ]
    assert "Iniciando análise de 2 tarefas." in caplog.messages
    assert "Análise concluída. Total de tarefas concluídas: 0." in caplog.messages


def test_completion_equal_to_deadline_is_not_late(analyzer: ModuleType) -> None:
    """Catch an inclusive late comparison where the SDD requires strict greater-than."""
    task = make_task(
        analyzer.Task,
        "20",
        "Conclusão no prazo exato",
        "Alta",
        "Concluída",
        datetime(2024, 1, 1, 8),
        datetime(2024, 1, 2, 8),
        datetime(2024, 1, 2, 8),
    )

    result = analyzer.analisar_tarefas([task])

    assert result["tempo_medio_conclusao_geral"] == 24.0
    assert result["taxa_atraso_geral"] == 0.0


def test_completed_task_without_completion_raises_custom_error(
    analyzer: ModuleType,
) -> None:
    """Catch completed records silently skipped when data_conclusao is absent."""
    task = make_task(
        analyzer.Task,
        "50",
        "Sem conclusão",
        "Baixa",
        "Concluída",
        datetime(2024, 1, 1, 8),
        datetime(2024, 1, 2, 8),
        None,
    )

    with pytest.raises(analyzer.DataInconsistenteError) as error:
        analyzer.analisar_tarefas([task])

    assert str(error.value) == (
        "Tarefa ID 50 apresenta inconsistência: data_conclusao está ausente."
    )


def test_completion_before_creation_raises_formatted_error_and_logs(
    analyzer: ModuleType, caplog: pytest.LogCaptureFixture
) -> None:
    """Catch invalid chronology and preserve the contract's date-bearing message."""
    task = make_task(
        analyzer.Task,
        "99",
        "Data de conclusão anterior à criação",
        "Alta",
        "Concluída",
        datetime(2024, 1, 10, 10),
        datetime(2024, 1, 12, 10),
        datetime(2024, 1, 9, 10),
    )

    with caplog.at_level(logging.ERROR, logger=analyzer.__name__):
        with pytest.raises(analyzer.DataInconsistenteError) as error:
            analyzer.analisar_tarefas([task])

    assert str(error.value) == (
        "Tarefa ID 99 apresenta inconsistência: data_conclusao "
        "(2024-01-09T10:00:00) é anterior à data_criacao "
        "(2024-01-10T10:00:00)."
    )
    assert caplog.messages == [
        "Tarefa ID 99 com data_conclusao anterior à data_criacao."
    ]


def test_missing_creation_or_deadline_raises_value_error_and_logs(
    analyzer: ModuleType, caplog: pytest.LogCaptureFixture
) -> None:
    """Catch completed tasks calculated without required creation/deadline dates."""
    for missing_field in ("data_criacao", "data_limite"):
        task = make_task(
            analyzer.Task,
            "60",
            "Data obrigatória ausente",
            "Média",
            "Concluída",
            None if missing_field == "data_criacao" else datetime(2024, 1, 1, 8),
            None if missing_field == "data_limite" else datetime(2024, 1, 2, 8),
            datetime(2024, 1, 2, 7),
        )

        with caplog.at_level(logging.ERROR, logger=analyzer.__name__):
            with pytest.raises(ValueError) as error:
                analyzer.analisar_tarefas([task])

        assert str(error.value) == (
            f"Tarefa ID 60 sem campo obrigatório: {missing_field}."
        )
        assert f"Tarefa ID 60 sem campo obrigatório: {missing_field}." in caplog.messages


@pytest.mark.parametrize(
    ("priority", "status"),
    [("Urgente", "Concluída"), ("Alta", "Em andamento"), ("Alta", "Concluida")],
)
def test_invalid_priority_or_status_raises_value_error(
    analyzer: ModuleType, priority: str, status: str
) -> None:
    """Catch values outside the fixed priority and status sets."""
    task = make_task(
        analyzer.Task,
        "70",
        "Valor inválido",
        priority,
        status,
        datetime(2024, 1, 1, 8),
        datetime(2024, 1, 2, 8),
        datetime(2024, 1, 2, 7),
    )

    with pytest.raises(ValueError):
        analyzer.analisar_tarefas([task])


def test_null_task_id_raises_value_error(analyzer: ModuleType) -> None:
    """Catch a Task whose required string identifier is null."""
    task = make_task(
        analyzer.Task,
        None,
        "Sem identificador",
        "Baixa",
        "Pendente",
        None,
        None,
        None,
    )

    with pytest.raises(ValueError):
        analyzer.analisar_tarefas([task])

def test_non_string_task_id_raises_value_error(analyzer: ModuleType) -> None:
    """Catch identifiers that violate the SDD's string field type."""
    task = make_task(
        analyzer.Task,
        70,
        "Identificador numérico",
        "Baixa",
        "Pendente",
        None,
        None,
        None,
    )

    with pytest.raises(ValueError):
        analyzer.analisar_tarefas([task])


def test_duplicate_task_ids_raise_value_error(analyzer: ModuleType) -> None:
    """Catch duplicate values where the Task contract requires unique identifiers."""
    task_type = analyzer.Task
    first_task = make_task(task_type, "80", "Primeira", "Baixa", "Pendente", None, None, None)
    second_task = make_task(task_type, "80", "Segunda", "Alta", "Pendente", None, None, None)

    with pytest.raises(ValueError):
        analyzer.analisar_tarefas([first_task, second_task])
