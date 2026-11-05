"""
SENTINEL X - Flask Endpoints Integration Tests
PRN: 202401110046
"""

import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_page_routes(client):
    routes = [
        ("/", b"SENTINEL X"),
        ("/scanner", b"Threat Intelligence Scanner"),
        ("/dashboard", b"Threat Analysis Dashboard"),
        ("/regex-lab", b"Regex Laboratory"),
        ("/automata", b"Regex to Automata Visualizer"),
        ("/simulator", b"DFA String Simulator"),
        ("/about", b"202401110046")
    ]
    for url, expected_content in routes:
        res = client.get(url)
        assert res.status_code == 200, f"Route {url} failed with status {res.status_code}"
        assert expected_content in res.data, f"Route {url} missing expected content"

def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ONLINE"
    assert data["student_prn"] == "202401110046"

def test_api_rules(client):
    res = client.get("/api/rules")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["count"] == 5

def test_api_scan_suspicious(client):
    payload = {"text": "admin' OR 1=1 --", "category": "all"}
    res = client.post("/api/scan", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["is_suspicious"] is True
    assert data["status"] == "SUSPICIOUS INDICATOR DETECTED"
    assert data["matched_rules_count"] >= 1

def test_api_scan_empty(client):
    payload = {"text": "   "}
    res = client.post("/api/scan", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False

def test_api_regex_test(client):
    payload = {"pattern": r"\w+@\w+\.\w+", "text": "contact: test@example.com"}
    res = client.post("/api/regex/test", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["match_count"] == 1

def test_api_automata_nfa(client):
    payload = {"pattern": "(a|b)*c"}
    res = client.post("/api/automata/nfa", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["automaton"]["type"] == "NFA"
    assert data["automaton"]["states_count"] == 10

def test_api_automata_dfa(client):
    payload = {"pattern": "(a|b)*c", "include_dead_state": True}
    res = client.post("/api/automata/dfa", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["dfa"]["type"] == "DFA"
    assert data["comparison"]["dfa_states_count"] > 0

def test_api_automata_minimize(client):
    payload = {"pattern": "(a|b)*c", "include_dead_state": True}
    res = client.post("/api/automata/minimize", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["minimized_dfa"]["states_count"] <= data["dfa"]["states_count"]
    assert data["minimized_dfa"]["states_reduced"] >= 0

def test_api_automata_simulate_accept(client):
    payload = {
        "pattern": "(a|b)*c",
        "input_string": "abbac",
        "automaton_type": "minimized"
    }
    res = client.post("/api/automata/simulate", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["simulation"]["accepted"] is True
    assert data["simulation"]["terminated_early"] is False

def test_api_automata_simulate_reject(client):
    payload = {
        "pattern": "(a|b)*c",
        "input_string": "abba",
        "automaton_type": "minimized"
    }
    res = client.post("/api/automata/simulate", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["simulation"]["accepted"] is False

