"""
freshness_checks.py
---------------------
Checagens de frescor (freshness) e completude (completeness) dos dados
- deliberadamente em Python puro, sem depender do Great Expectations
nem do pandas. Essas duas dimensoes de qualidade nao sao sobre o valor
de uma coluna isolada; sao sobre a forma da carga como um todo, e uma
funcao pura testa isso melhor do que uma expectation generica.

Fica lado a lado com as expectations do GX em quality_runner.py, mas
sao conceitualmente diferentes: GX valida linhas; este modulo valida
"a carga de hoje chegou e esta completa".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass
class CheckResult:
    name: str
    category: str  # "freshness" ou "completeness"
    success: bool
    details: str


def check_freshness(
    measured_dates: list[str],
    reference_date: date,
    max_staleness_days: int = 1,
) -> CheckResult:
    """Verifica se a data mais recente presente nos dados esta dentro
    da janela aceitavel de atraso em relacao a `reference_date`.

    Um pipeline que roda e nao falha, mas processa dados de 5 dias
    atras sem avisar ninguem, e um tipo de falha silenciosa tao grave
    quanto um erro que quebra a execucao.
    """
    if not measured_dates:
        return CheckResult(
            name="freshness",
            category="freshness",
            success=False,
            details="Nenhuma data encontrada nos dados - carga vazia ou ausente.",
        )

    latest = max(_parse_date(d) for d in measured_dates)
    staleness_days = (reference_date - latest).days

    success = staleness_days <= max_staleness_days
    details = (
        f"Data mais recente: {latest.isoformat()} "
        f"({staleness_days} dia(s) atras de {reference_date.isoformat()}, "
        f"limite: {max_staleness_days})"
    )
    return CheckResult(name="freshness", category="freshness", success=success, details=details)


def check_completeness(
    present_combinations: set[tuple[str, str]],
    expected_combinations: set[tuple[str, str]],
) -> CheckResult:
    """Verifica se todas as combinacoes esperadas de (cidade, poluente)
    estao presentes na carga mais recente.

    Diferente de um `not_null` de coluna: aqui a pergunta e "faltou uma
    cidade inteira hoje?", nao "algum valor individual esta nulo?".
    """
    missing = expected_combinations - present_combinations

    success = len(missing) == 0
    if success:
        details = f"Todas as {len(expected_combinations)} combinacoes esperadas estao presentes."
    else:
        missing_str = ", ".join(f"{city}/{parameter}" for city, parameter in sorted(missing))
        details = f"Faltando {len(missing)} combinacao(oes): {missing_str}"

    return CheckResult(name="completeness", category="completeness", success=success, details=details)


def _parse_date(value: str | date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
