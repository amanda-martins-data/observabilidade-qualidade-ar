"""
quality_runner.py
-------------------
Orquestra a validacao completa da camada Gold:
  1. Roda as expectations do Great Expectations (schema/valor por linha).
  2. Roda as checagens de freshness e completeness (forma da carga).
  3. Devolve uma lista unica de resultados, no mesmo formato, pronta
     para virar JSON ou HTML (ver report_generator.py).

Decisao de design: GX valida LINHAS; freshness_checks valida a CARGA
como um todo. Sao categorias de problema diferentes, e um pipeline
pode passar em uma e falhar na outra - por isso ficam sempre juntas
no mesmo relatorio, nunca escondidas uma da outra.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date

import great_expectations as gx
import pandas as pd

from expectations_suite import build_expectations
from freshness_checks import check_completeness, check_freshness


@dataclass
class CheckReport:
    name: str
    category: str
    success: bool
    details: str


def _run_schema_expectations(df: pd.DataFrame) -> list[CheckReport]:
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas("gold")
    asset = data_source.add_dataframe_asset("air_quality_daily")
    batch_def = asset.add_batch_definition_whole_dataframe("batch")
    batch = batch_def.get_batch(batch_parameters={"dataframe": df})

    reports = []
    for name, expectation in build_expectations():
        result = batch.validate(expectation)
        unexpected = result.result.get("unexpected_count", 0) if result.result else 0
        details = "OK" if result.success else f"{unexpected} linha(s) fora do esperado"
        reports.append(CheckReport(name=name, category="schema", success=bool(result.success), details=details))

    return reports


def run_quality_checks(
    df: pd.DataFrame,
    reference_date: date,
    expected_combinations: set[tuple[str, str]],
    max_staleness_days: int = 1,
) -> list[CheckReport]:
    """Ponto de entrada principal. `df` deve ter o schema da camada
    Gold (city, parameter, avg_value, reading_count, min_value,
    max_value, aqi_category_pm25, measured_date)."""
    reports = _run_schema_expectations(df)

    freshness = check_freshness(
        df["measured_date"].astype(str).tolist(),
        reference_date=reference_date,
        max_staleness_days=max_staleness_days,
    )
    reports.append(CheckReport(**asdict(freshness)))

    latest_date = df["measured_date"].astype(str).max()
    latest_rows = df[df["measured_date"].astype(str) == latest_date]
    present = set(zip(latest_rows["city"], latest_rows["parameter"]))

    completeness = check_completeness(present, expected_combinations)
    reports.append(CheckReport(**asdict(completeness)))

    return reports
