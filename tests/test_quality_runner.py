"""
Testes de quality_runner.py - rodam o Great Expectations DE VERDADE,
via contexto efemero (em memoria, sem persistir nada em disco e sem
precisar de rede). Nao ha necessidade de mockar o GX: o contexto
efemero e rapido o suficiente para rodar em um teste unitario.
"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quality_runner import run_quality_checks

VALID_ROW = {
    "city": "Sao Paulo",
    "parameter": "pm25",
    "unit": "ug/m3",
    "measured_date": "2026-01-05",
    "reading_count": 16,
    "avg_value": 30.0,
    "min_value": 10.0,
    "max_value": 50.0,
    "aqi_category_pm25": "Moderada",
}


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_all_checks_pass_on_clean_data():
    df = _df([VALID_ROW])
    expected = {("Sao Paulo", "pm25")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    assert all(r.success for r in results)
    assert len(results) == 10  # 8 expectations do GX + freshness + completeness


def test_detects_invalid_parameter():
    row = {**VALID_ROW, "parameter": "gas_desconhecido"}
    df = _df([row])
    expected = {("Sao Paulo", "gas_desconhecido")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    failed_names = [r.name for r in results if not r.success]
    assert "parameter deve ser um poluente conhecido" in failed_names


def test_detects_negative_avg_value():
    row = {**VALID_ROW, "avg_value": -5.0}
    df = _df([row])
    expected = {("Sao Paulo", "pm25")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    failed_names = [r.name for r in results if not r.success]
    assert "avg_value deve estar num intervalo plausivel" in failed_names


def test_detects_min_greater_than_max():
    row = {**VALID_ROW, "min_value": 100.0, "max_value": 10.0}
    df = _df([row])
    expected = {("Sao Paulo", "pm25")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    failed_names = [r.name for r in results if not r.success]
    assert "min_value nao pode ser maior que max_value" in failed_names


def test_stale_data_fails_freshness_but_not_schema():
    row = {**VALID_ROW, "measured_date": "2025-01-01"}
    df = _df([row])
    expected = {("Sao Paulo", "pm25")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    freshness_result = next(r for r in results if r.category == "freshness")
    schema_results = [r for r in results if r.category == "schema"]

    assert freshness_result.success is False
    assert all(r.success for r in schema_results)


def test_missing_city_fails_completeness_only():
    df = _df([VALID_ROW])
    expected = {("Sao Paulo", "pm25"), ("Belo Horizonte", "pm25")}

    results = run_quality_checks(df, reference_date=date(2026, 1, 5), expected_combinations=expected)

    completeness_result = next(r for r in results if r.category == "completeness")
    assert completeness_result.success is False
    assert "Belo Horizonte/pm25" in completeness_result.details
