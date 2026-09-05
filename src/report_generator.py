"""
report_generator.py
---------------------
Gera um dashboard HTML estatico, autocontido (sem JS externo, sem
dependencia de rede) a partir da lista de CheckReport produzida por
quality_runner.py.

Decisao de design: nao usa nenhum emoji nem icone - status e sempre
comunicado por texto ("PASS"/"FAIL") mais cor, para funcionar bem em
qualquer terminal, leitor de tela ou impressao em preto e branco.
"""

from __future__ import annotations

from datetime import datetime

from quality_runner import CheckReport

_STYLE = """
body { font-family: -apple-system, Segoe UI, Arial, sans-serif; margin: 2rem; background: #0f1115; color: #e6e6e6; }
h1 { font-size: 1.4rem; margin-bottom: 0.25rem; }
.subtitle { color: #9aa0a6; margin-bottom: 1.5rem; font-size: 0.9rem; }
.summary { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.card { border: 1px solid #2a2d34; border-radius: 8px; padding: 1rem 1.5rem; }
.card .value { font-size: 1.8rem; font-weight: 600; }
.card.total .value { color: #e6e6e6; }
.card.pass .value { color: #4caf50; }
.card.fail .value { color: #e05252; }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 0.6rem 0.8rem; border-bottom: 1px solid #2a2d34; font-size: 0.9rem; }
th { color: #9aa0a6; font-weight: 500; text-transform: uppercase; font-size: 0.75rem; }
.status { font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 4px; display: inline-block; }
.status.pass { color: #4caf50; background: rgba(76, 175, 80, 0.12); }
.status.fail { color: #e05252; background: rgba(224, 82, 82, 0.12); }
.category { color: #9aa0a6; font-size: 0.8rem; text-transform: uppercase; }
"""


def generate_html_report(results: list[CheckReport], generated_at: datetime | None = None) -> str:
    generated_at = generated_at or datetime.now()
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed

    rows = "\n".join(
        f"""
        <tr>
            <td class="category">{r.category}</td>
            <td>{r.name}</td>
            <td><span class="status {'pass' if r.success else 'fail'}">{'PASS' if r.success else 'FAIL'}</span></td>
            <td>{r.details}</td>
        </tr>
        """
        for r in results
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<title>Relatorio de Qualidade de Dados</title>
<style>{_STYLE}</style>
</head>
<body>
<h1>Relatorio de Qualidade de Dados - air_quality_daily</h1>
<div class="subtitle">Gerado em {generated_at.strftime('%Y-%m-%d %H:%M:%S')}</div>

<div class="summary">
    <div class="card total"><div class="value">{total}</div><div>Checagens</div></div>
    <div class="card pass"><div class="value">{passed}</div><div>Passaram</div></div>
    <div class="card fail"><div class="value">{failed}</div><div>Falharam</div></div>
</div>

<table>
    <thead>
        <tr><th>Categoria</th><th>Checagem</th><th>Status</th><th>Detalhes</th></tr>
    </thead>
    <tbody>
        {rows}
    </tbody>
</table>
</body>
</html>
"""
