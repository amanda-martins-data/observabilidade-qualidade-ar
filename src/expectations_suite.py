"""
expectations_suite.py
-----------------------
Define QUAIS regras de qualidade se aplicam a camada Gold
(air_quality_daily, dos Projetos 03/04) - separado de COMO elas sao
executadas (isso fica em quality_runner.py).

Cada expectation e nomeada explicitamente, para que o relatorio final
mostre "reading_count deve ser maior que zero" em vez de um nome de
classe generico do Great Expectations.
"""

from __future__ import annotations

import great_expectations as gx

VALID_PARAMETERS = ["pm25", "pm10", "o3", "no2", "co"]
VALID_AQI_CATEGORIES = [
    "Boa",
    "Moderada",
    "Insalubre p/ grupos sensiveis",
    "Insalubre",
    "Muito insalubre",
]

MAX_PLAUSIBLE_VALUE = 1000.0  # limite de sanidade; nao e um limite regulatorio de AQI


def build_expectations() -> list[tuple[str, "gx.expectations.Expectation"]]:
    """Retorna pares (nome_legivel, expectation) para rodar contra a
    camada Gold. A ordem importa para a leitura do relatorio final."""
    return [
        (
            "city nao pode ser nulo",
            gx.expectations.ExpectColumnValuesToNotBeNull(column="city"),
        ),
        (
            "parameter nao pode ser nulo",
            gx.expectations.ExpectColumnValuesToNotBeNull(column="parameter"),
        ),
        (
            "parameter deve ser um poluente conhecido",
            gx.expectations.ExpectColumnValuesToBeInSet(column="parameter", value_set=VALID_PARAMETERS),
        ),
        (
            "avg_value nao pode ser nulo",
            gx.expectations.ExpectColumnValuesToNotBeNull(column="avg_value"),
        ),
        (
            "avg_value deve estar num intervalo plausivel",
            gx.expectations.ExpectColumnValuesToBeBetween(
                column="avg_value", min_value=0, max_value=MAX_PLAUSIBLE_VALUE
            ),
        ),
        (
            "reading_count deve ser maior que zero",
            gx.expectations.ExpectColumnValuesToBeBetween(column="reading_count", min_value=1),
        ),
        (
            "min_value nao pode ser maior que max_value",
            gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(
                column_A="max_value", column_B="min_value", or_equal=True
            ),
        ),
        (
            "aqi_category_pm25 deve ser uma categoria valida (quando preenchida)",
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="aqi_category_pm25", value_set=VALID_AQI_CATEGORIES, mostly=1.0
            ),
        ),
    ]
