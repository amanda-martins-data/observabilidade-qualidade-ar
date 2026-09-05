"""
run_quality_checks.py
-----------------------
Ponto de entrada CLI: le a camada Gold (JSON, mesma estrutura dos
Projetos 03/04), roda as checagens de qualidade e escreve dois
artefatos: um relatorio JSON (consumivel por outro sistema, como o
agente de qualidade do Projeto 05) e um dashboard HTML.

Uso:
    python src/run_quality_checks.py caminho/para/air_quality_daily.json cidade1,cidade2 --saida ./out
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from quality_runner import run_quality_checks
from report_generator import generate_html_report

DEFAULT_CITIES = ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte"]
DEFAULT_PARAMETERS = ["pm25", "pm10", "o3", "no2", "co"]


def _expected_combinations(cities: list[str], parameters: list[str]) -> set[tuple[str, str]]:
    return {(city, parameter) for city in cities for parameter in parameters}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roda checagens de qualidade sobre a camada Gold.")
    parser.add_argument("gold_path", type=str, help="Caminho para o JSON da camada Gold.")
    parser.add_argument("--cidades", type=str, default=",".join(DEFAULT_CITIES))
    parser.add_argument("--poluentes", type=str, default=",".join(DEFAULT_PARAMETERS))
    parser.add_argument("--max-atraso-dias", type=int, default=1)
    parser.add_argument("--saida", type=str, default="./out")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rows = json.loads(Path(args.gold_path).read_text(encoding="utf-8"))
    df = pd.DataFrame(rows)

    cities = [c.strip() for c in args.cidades.split(",") if c.strip()]
    parameters = [p.strip() for p in args.poluentes.split(",") if p.strip()]
    expected = _expected_combinations(cities, parameters)

    results = run_quality_checks(
        df,
        reference_date=date.today(),
        expected_combinations=expected,
        max_staleness_days=args.max_atraso_dias,
    )

    out_dir = Path(args.saida)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_json = {
        "generated_at": datetime.now().isoformat(),
        "total": len(results),
        "passed": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "checks": [asdict(r) for r in results],
    }
    (out_dir / "report.json").write_text(json.dumps(report_json, ensure_ascii=False, indent=2), encoding="utf-8")

    html = generate_html_report(results)
    (out_dir / "report.html").write_text(html, encoding="utf-8")

    failed_count = report_json["failed"]
    print(f"Checagens: {report_json['total']} | Passaram: {report_json['passed']} | Falharam: {failed_count}")
    print(f"Relatorios escritos em {out_dir}/report.json e {out_dir}/report.html")

    if failed_count > 0:
        exit(1)


if __name__ == "__main__":
    main()
