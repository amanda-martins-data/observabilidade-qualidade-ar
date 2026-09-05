"""
Testes de freshness_checks.py - 100% offline, sem GX, sem pandas.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from freshness_checks import check_completeness, check_freshness


def test_freshness_passes_when_within_limit():
    result = check_freshness(
        ["2026-01-05", "2026-01-04"],
        reference_date=date(2026, 1, 5),
        max_staleness_days=1,
    )

    assert result.success is True
    assert result.category == "freshness"


def test_freshness_fails_when_stale():
    result = check_freshness(
        ["2026-01-01"],
        reference_date=date(2026, 1, 5),
        max_staleness_days=1,
    )

    assert result.success is False
    assert "4 dia" in result.details


def test_freshness_fails_on_empty_data():
    result = check_freshness([], reference_date=date(2026, 1, 5), max_staleness_days=1)

    assert result.success is False
    assert "vazia" in result.details or "ausente" in result.details


def test_freshness_accepts_exact_limit_as_success():
    result = check_freshness(
        ["2026-01-04"],
        reference_date=date(2026, 1, 5),
        max_staleness_days=1,
    )

    assert result.success is True


def test_completeness_passes_when_all_present():
    present = {("Sao Paulo", "pm25"), ("Rio de Janeiro", "pm25")}
    expected = {("Sao Paulo", "pm25"), ("Rio de Janeiro", "pm25")}

    result = check_completeness(present, expected)

    assert result.success is True
    assert result.category == "completeness"


def test_completeness_fails_when_missing_combination():
    present = {("Sao Paulo", "pm25")}
    expected = {("Sao Paulo", "pm25"), ("Belo Horizonte", "pm25")}

    result = check_completeness(present, expected)

    assert result.success is False
    assert "Belo Horizonte/pm25" in result.details


def test_completeness_ignores_extra_unexpected_combinations():
    """Combinacoes a mais nao sao um problema de completude - so as
    que faltam. Dado extra nao e o mesmo tipo de falha que dado ausente."""
    present = {("Sao Paulo", "pm25"), ("Sao Paulo", "pm10")}
    expected = {("Sao Paulo", "pm25")}

    result = check_completeness(present, expected)

    assert result.success is True
