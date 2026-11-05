"""
SENTINEL X - Regex Threat Detection Engine Tests
PRN: 202401110046
"""

import pytest
import re
from backend.detection_rules import DETECTION_RULES, get_rule_by_id
from backend.regex_engine import scan_text, test_custom_regex as run_custom_regex, STATUS_SUSPICIOUS, STATUS_NO_MATCH

def test_all_five_rules_exist():
    assert len(DETECTION_RULES) == 5
    rule_ids = [r["id"] for r in DETECTION_RULES]
    assert "RULE-01" in rule_ids
    assert "RULE-02" in rule_ids
    assert "RULE-03" in rule_ids
    assert "RULE-04" in rule_ids
    assert "RULE-05" in rule_ids

@pytest.mark.parametrize("rule", DETECTION_RULES)
def test_five_matching_cases_per_rule(rule):
    pattern = re.compile(rule["pattern"])
    assert len(rule["matching_cases"]) == 5, f"{rule['id']} must have exactly 5 matching cases"
    for test_str in rule["matching_cases"]:
        match = pattern.search(test_str)
        assert match is not None, f"Expected match for rule {rule['id']} with string: '{test_str}'"

@pytest.mark.parametrize("rule", DETECTION_RULES)
def test_five_non_matching_cases_per_rule(rule):
    pattern = re.compile(rule["pattern"])
    assert len(rule["non_matching_cases"]) == 5, f"{rule['id']} must have exactly 5 non-matching cases"
    for test_str in rule["non_matching_cases"]:
        match = pattern.search(test_str)
        assert match is None, f"Expected NO match for rule {rule['id']} with string: '{test_str}'"

def test_scan_text_suspicious():
    payload = "admin' OR 1=1 -- <script>alert(1)</script>"
    res = scan_text(payload)
    assert res["is_suspicious"] is True
    assert res["status"] == STATUS_SUSPICIOUS
    assert res["matched_rules_count"] == 2
    assert "SQL Injection Indicators" in [r["name"] for r in res["matched_rules"]]
    assert "Script Injection Indicators" in [r["name"] for r in res["matched_rules"]]
    assert "<mark class=\"threat-highlight\"" in res["highlighted_html"]

def test_scan_text_clean():
    payload = "Hello, welcome to our academic portal."
    res = scan_text(payload)
    assert res["is_suspicious"] is False
    assert res["status"] == STATUS_NO_MATCH
    assert res["matched_rules_count"] == 0
    assert len(res["matched_rules"]) == 0
    assert "<mark" not in res["highlighted_html"]

def test_custom_regex_evaluation():
    res = run_custom_regex(r"\d+", "User ID: 12345, Score: 99")
    assert res["valid"] is True
    assert res["match_count"] == 2
    assert res["matches"][0]["matched_text"] == "12345"
    assert res["matches"][1]["matched_text"] == "99"

def test_custom_regex_invalid_syntax():
    res = run_custom_regex(r"(abc[", "test text")
    assert res["valid"] is False
    assert "Regex Compilation Error" in res["error"]
