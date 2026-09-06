"""
Testes de report_generator.py - validam o HTML gerado sem precisar de
um navegador (checagem de strings, nao de renderizacao visual).
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quality_runner import CheckReport
from report_generator import generate_html_report


def test_report_includes_summary_counts():
    results = [
        CheckReport(name="a", category="schema", success=True, details="OK"),
        CheckReport(name="b", category="schema", success=False, details="quebrou"),
    ]

    html = generate_html_report(results, generated_at=datetime(2026, 1, 5, 10, 0, 0))

    assert ">2<" in html  # total
    assert ">1<" in html  # passou / falhou (aparece duas vezes, uma para cada)


def test_report_marks_failures_as_fail_and_passes_as_pass():
    results = [
        CheckReport(name="check ok", category="schema", success=True, details="OK"),
        CheckReport(name="check quebrado", category="schema", success=False, details="deu ruim"),
    ]

    html = generate_html_report(results)

    assert 'class="status pass">PASS' in html
    assert 'class="status fail">FAIL' in html


def test_report_contains_no_emoji():
    """Regra do projeto: nada de emoji em codigo/artefatos gerados -
    status e comunicado por texto (PASS/FAIL) e cor, nao por icone."""
    results = [
        CheckReport(name="check", category="freshness", success=False, details="atrasado"),
    ]

    html = generate_html_report(results)

    # Nenhum caractere fora do plano basico multilingue (onde vivem emojis)
    assert all(ord(ch) < 0x1F000 for ch in html)


def test_report_includes_check_details_and_category():
    results = [
        CheckReport(name="freshness", category="freshness", success=False, details="5 dias atrasado"),
    ]

    html = generate_html_report(results)

    assert "freshness" in html
    assert "5 dias atrasado" in html
