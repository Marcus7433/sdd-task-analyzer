"""Calculate the TaskAnalyzer metrics defined by the project SDD."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES: tuple[str, ...] = ("Baixa", "Média", "Alta")
STATUS_PENDENTE = "Pendente"
STATUS_CONCLUIDA = "Concluída"


@dataclass
class Task:
    """Represent a task submitted to the analyzer.

    Args:
        id: Unique string identifier.
        titulo: Task title or description.
        prioridade: One of ``Baixa``, ``Média``, or ``Alta``.
        status: ``Pendente`` or ``Concluída``.
        data_criacao: Creation time; required for completed tasks.
        data_limite: Deadline; required for completed tasks.
        data_conclusao: Completion time; absent only for pending tasks.
    """

    id: str
    titulo: str
    prioridade: str
    status: str
    data_criacao: datetime | None = None
    data_limite: datetime | None = None
    data_conclusao: datetime | None = None


class DataInconsistenteError(ValueError):
    """Raised when a completed task has missing or inconsistent chronology."""


def _validar_tarefa(tarefa: Task) -> None:
    """Validate a task's declared fields and completed-task date contract.

    Args:
        tarefa: Task to validate.

    Raises:
        ValueError: If a field has an invalid type or allowed value, or a
            completed task lacks its creation time or deadline.
        DataInconsistenteError: If completion is missing for a completed task
            or precedes creation.
    """
    if not isinstance(tarefa.id, str):
        raise ValueError("O campo id deve ser uma string não nula.")
    if not isinstance(tarefa.titulo, str):
        raise ValueError(f"Tarefa ID {tarefa.id} possui titulo inválido.")
    if tarefa.prioridade not in PRIORIDADES:
        raise ValueError(f"Tarefa ID {tarefa.id} possui prioridade inválida.")
    if tarefa.status not in (STATUS_PENDENTE, STATUS_CONCLUIDA):
        raise ValueError(f"Tarefa ID {tarefa.id} possui status inválido.")

    if tarefa.status == STATUS_PENDENTE:
        if tarefa.data_conclusao is not None:
            raise ValueError(
                f"Tarefa ID {tarefa.id} pendente não pode ter data_conclusao."
            )
        return

    if tarefa.data_criacao is None:
        logger.error("Tarefa ID %s sem campo obrigatório: data_criacao.", tarefa.id)
        raise ValueError(f"Tarefa ID {tarefa.id} sem campo obrigatório: data_criacao.")
    if tarefa.data_limite is None:
        logger.error("Tarefa ID %s sem campo obrigatório: data_limite.", tarefa.id)
        raise ValueError(f"Tarefa ID {tarefa.id} sem campo obrigatório: data_limite.")
    if tarefa.data_conclusao is None:
        logger.error("Tarefa ID %s sem campo obrigatório: data_conclusao.", tarefa.id)
        raise DataInconsistenteError(
            f"Tarefa ID {tarefa.id} apresenta inconsistência: "
            "data_conclusao está ausente."
        )

    for campo in ("data_criacao", "data_limite", "data_conclusao"):
        if not isinstance(getattr(tarefa, campo), datetime):
            raise ValueError(f"Tarefa ID {tarefa.id} possui {campo} inválida.")

    if tarefa.data_conclusao < tarefa.data_criacao:
        logger.error(
            "Tarefa ID %s com data_conclusao anterior à data_criacao.", tarefa.id
        )
        raise DataInconsistenteError(
            f"Tarefa ID {tarefa.id} apresenta inconsistência: "
            f"data_conclusao ({tarefa.data_conclusao.isoformat()}) é anterior à "
            f"data_criacao ({tarefa.data_criacao.isoformat()})."
        )


def _filtrar_concluidas(tarefas: list[Task]) -> list[Task]:
    """Return completed tasks and warn for each pending task ignored.

    Args:
        tarefas: Tasks already validated by the analyzer.

    Returns:
        Tasks whose status is ``Concluída``.
    """
    concluidas: list[Task] = []
    for tarefa in tarefas:
        if tarefa.status == STATUS_CONCLUIDA:
            concluidas.append(tarefa)
        else:
            logger.warning("Tarefa ID %s ignorada (status=Pendente).", tarefa.id)
    return concluidas


def _calcular_tempo_conclusao(tarefa: Task) -> float:
    """Return elapsed creation-to-completion time in hours.

    Args:
        tarefa: Validated completed task.

    Returns:
        Elapsed time in hours without rounding.
    """
    assert tarefa.data_criacao is not None and tarefa.data_conclusao is not None
    delta = tarefa.data_conclusao - tarefa.data_criacao
    return delta.total_seconds() / 3600.0


def _calcular_atraso(tarefa: Task) -> bool:
    """Return whether completion occurred strictly after the deadline.

    Args:
        tarefa: Validated completed task.

    Returns:
        ``True`` when completion is later than the deadline.
    """
    assert tarefa.data_limite is not None and tarefa.data_conclusao is not None
    return tarefa.data_conclusao > tarefa.data_limite


def _inicializar_indicadores_vazios() -> dict[str, dict[str, int | float]]:
    """Create zero-valued indicators for each fixed priority.

    Returns:
        The priority metrics structure with all counts and rates set to zero.
    """
    return {
        prioridade: {
            "total_tarefas_concluidas": 0,
            "tempo_medio_conclusao": 0.0,
            "taxa_atraso": 0.0,
        }
        for prioridade in PRIORIDADES
    }


def _calcular_indicadores(tarefas: list[Task]) -> dict[str, Any]:
    """Calculate global and per-priority metrics for completed tasks.

    Args:
        tarefas: Validated completed tasks.

    Returns:
        The exact metrics mapping required by the SDD.
    """
    total = len(tarefas)
    tempos = [_calcular_tempo_conclusao(tarefa) for tarefa in tarefas]
    atrasadas = sum(_calcular_atraso(tarefa) for tarefa in tarefas)
    por_prioridade = _inicializar_indicadores_vazios()

    for prioridade in PRIORIDADES:
        grupo = [tarefa for tarefa in tarefas if tarefa.prioridade == prioridade]
        if not grupo:
            logger.warning("Nenhuma tarefa concluída com prioridade %s.", prioridade)
            continue
        horas = [_calcular_tempo_conclusao(tarefa) for tarefa in grupo]
        atrasadas_grupo = sum(_calcular_atraso(tarefa) for tarefa in grupo)
        por_prioridade[prioridade] = {
            "total_tarefas_concluidas": len(grupo),
            "tempo_medio_conclusao": sum(horas) / len(grupo),
            "taxa_atraso": (atrasadas_grupo / len(grupo)) * 100.0,
        }

    return {
        "total_tarefas_concluidas": total,
        "tempo_medio_conclusao_geral": sum(tempos) / total if total else 0.0,
        "taxa_atraso_geral": (atrasadas / total) * 100.0 if total else 0.0,
        "indicadores_por_prioridade": por_prioridade,
    }


def analisar_tarefas(tarefas: list[Task]) -> dict:
    """Analyze tasks and return the SDD productivity metrics.

    Args:
        tarefas: Tasks containing the fields declared by :class:`Task`.

    Returns:
        Exactly the global and per-priority metric keys specified by the SDD.

    Raises:
        DataInconsistenteError: If a completed task has a missing completion
            date or completion precedes creation.
        ValueError: If task data violates the declared contract.
    """
    logger.info("Iniciando análise de %s tarefas.", len(tarefas))
    ids: set[str] = set()
    for tarefa in tarefas:
        _validar_tarefa(tarefa)
        if tarefa.id in ids:
            raise ValueError(f"Identificador de tarefa duplicado: {tarefa.id}.")
        ids.add(tarefa.id)

    concluidas = _filtrar_concluidas(tarefas)
    resultado = _calcular_indicadores(concluidas)
    logger.info(
        "Análise concluída. Total de tarefas concluídas: %s.",
        resultado["total_tarefas_concluidas"],
    )
    return resultado
