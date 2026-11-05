"""
SENTINEL X — Interactive Regex-Based Cybersecurity Threat Detection & Automata Visualization Platform
Assigned Application Domain: Cybersecurity
Student PRN: 202401110046
Flask Application Server
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.detection_rules import DETECTION_RULES, get_rule_by_id, get_rules_by_category
from backend.regex_engine import scan_text, test_custom_regex, ACADEMIC_DISCLAIMER
from backend.regex_parser import RegexParseError
from backend.thompson_nfa import build_nfa_from_regex
from backend.subset_construction import nfa_to_dfa
from backend.dfa_minimization import minimize_dfa
from backend.simulator import simulate_dfa

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB maximum payload

STUDENT_INFO = {
    "project_name": "SENTINEL X",
    "project_title": "Interactive Regex-Based Cybersecurity Threat Detection & Automata Visualization Platform",
    "student_prn": "202401110046",
    "domain": "Cybersecurity",
    "academic_year": "2024-2026",
    "core_concepts": [
        "Regular Expressions (RE)",
        "Nondeterministic Finite Automata (NFA)",
        "Deterministic Finite Automata (DFA)",
        "Thompson's Construction",
        "Subset Construction (Powerset Construction)",
        "DFA Minimization (Partition Refinement / Hopcroft's)",
        "Regular Languages & Chomsky Hierarchy",
        "Cybersecurity Pattern Recognition"
    ]
}

# Context processor to inject student info into all templates
@app.context_processor
def inject_global_data():
    return {
        "student_info": STUDENT_INFO,
        "current_year": datetime.now().year,
        "disclaimer": ACADEMIC_DISCLAIMER
    }

# ================= PAGE ROUTES =================

@app.route("/")
def index():
    """Landing Page (Phase 1)"""
    return render_template("index.html", active_page="home")

@app.route("/scanner")
def scanner():
    """Threat Input / Scanner Page (Phase 2)"""
    return render_template("scanner.html", active_page="scanner")

@app.route("/dashboard")
def dashboard():
    """Threat Analysis Dashboard (Phase 4)"""
    return render_template("dashboard.html", active_page="dashboard")

@app.route("/regex-lab")
def regex_lab():
    """Regex Laboratory (Phase 5)"""
    return render_template("regex_lab.html", active_page="regex_lab", rules=DETECTION_RULES)

@app.route("/automata")
def automata_studio():
    """Automata Studio — Regex to NFA, DFA, and Minimized DFA (Phases 6 & 7)"""
    return render_template("automata.html", active_page="automata")

@app.route("/simulator")
def dfa_simulator():
    """Interactive DFA String Simulator (Phase 8)"""
    return render_template("simulator.html", active_page="simulator")

@app.route("/about")
def about():
    """About & Academic Documentation Page (Phase 9)"""
    return render_template("about.html", active_page="about", rules=DETECTION_RULES)

# ================= REST API ENDPOINTS =================

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ONLINE",
        "service": "SENTINEL X Threat Intelligence & Automata Engine",
        "timestamp": datetime.now().isoformat(),
        "student_prn": STUDENT_INFO["student_prn"],
        "version": "1.0.0"
    }), 200

@app.route("/api/rules", methods=["GET"])
def get_rules():
    """Retrieve all configured detection rules."""
    category = request.args.get("category", "all")
    rules = get_rules_by_category(category)
    return jsonify({
        "success": True,
        "count": len(rules),
        "rules": rules
    }), 200

@app.route("/api/scan", methods=["POST"])
def scan_endpoint():
    """
    Threat scanning endpoint (Phase 3).
    Evaluates input text against configured rules.
    """
    try:
        data = request.get_json(silent=True) or {}
        input_text = data.get("text", "")
        category = data.get("category", "all")

        if not input_text or not input_text.strip():
            return jsonify({
                "success": False,
                "error": "Input text cannot be empty."
            }), 400

        result = scan_text(input_text, category)
        return jsonify({
            "success": True,
            **result
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal scan error: {str(e)}"
        }), 500

@app.route("/api/regex/test", methods=["POST"])
def regex_test_endpoint():
    """
    Interactive Custom Regex Tester (Phase 5).
    """
    try:
        data = request.get_json(silent=True) or {}
        pattern = data.get("pattern", "")
        text = data.get("text", "")
        case_sensitive = data.get("case_sensitive", True)

        result = test_custom_regex(pattern, text, case_sensitive)
        return jsonify(result), 200 if result.get("valid") else 400
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": f"Regex evaluation error: {str(e)}"
        }), 500

@app.route("/api/automata/nfa", methods=["POST"])
def automata_nfa_endpoint():
    """
    Constructs an NFA using Thompson's Construction (Phase 6).
    """
    try:
        data = request.get_json(silent=True) or {}
        pattern = data.get("pattern", "")

        if not pattern or not pattern.strip():
            return jsonify({
                "success": False,
                "error": "Regular expression pattern is required."
            }), 400

        nfa = build_nfa_from_regex(pattern.strip())
        nfa_dict = nfa.to_dict()

        return jsonify({
            "success": True,
            "pattern": pattern,
            "automaton": nfa_dict
        }), 200
    except RegexParseError as e:
        return jsonify({
            "success": False,
            "error": f"Syntax Error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"NFA Generation Error: {str(e)}"
        }), 500

@app.route("/api/automata/dfa", methods=["POST"])
def automata_dfa_endpoint():
    """
    Converts regex to NFA and then to DFA using Subset Construction (Phase 7).
    """
    try:
        data = request.get_json(silent=True) or {}
        pattern = data.get("pattern", "")
        include_dead_state = data.get("include_dead_state", True)

        if not pattern or not pattern.strip():
            return jsonify({
                "success": False,
                "error": "Regular expression pattern is required."
            }), 400

        nfa = build_nfa_from_regex(pattern.strip())
        dfa = nfa_to_dfa(nfa, include_dead_state=include_dead_state)

        nfa_dict = nfa.to_dict()
        dfa_dict = dfa.to_dict()

        comparison = {
            "nfa_states_count": nfa_dict["states_count"],
            "nfa_transitions_count": nfa_dict["transitions_count"],
            "dfa_states_count": dfa_dict["states_count"],
            "dfa_transitions_count": dfa_dict["transitions_count"],
            "dfa_start_state": dfa_dict["start_state"],
            "dfa_accept_states": dfa_dict["accept_states"],
            "dead_state": dfa_dict["dead_state"]
        }

        return jsonify({
            "success": True,
            "pattern": pattern,
            "nfa": nfa_dict,
            "dfa": dfa_dict,
            "comparison": comparison
        }), 200
    except RegexParseError as e:
        return jsonify({
            "success": False,
            "error": f"Syntax Error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"DFA Conversion Error: {str(e)}"
        }), 500

@app.route("/api/automata/minimize", methods=["POST"])
def automata_minimize_endpoint():
    """
    Minimizes the DFA using partition refinement (Phase 7).
    """
    try:
        data = request.get_json(silent=True) or {}
        pattern = data.get("pattern", "")
        include_dead_state = data.get("include_dead_state", True)

        if not pattern or not pattern.strip():
            return jsonify({
                "success": False,
                "error": "Regular expression pattern is required."
            }), 400

        nfa = build_nfa_from_regex(pattern.strip())
        dfa = nfa_to_dfa(nfa, include_dead_state=include_dead_state)
        min_dfa_dict = minimize_dfa(dfa)

        return jsonify({
            "success": True,
            "pattern": pattern,
            "nfa": nfa.to_dict(),
            "dfa": dfa.to_dict(),
            "minimized_dfa": min_dfa_dict
        }), 200
    except RegexParseError as e:
        return jsonify({
            "success": False,
            "error": f"Syntax Error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Minimization Error: {str(e)}"
        }), 500

@app.route("/api/automata/simulate", methods=["POST"])
def automata_simulate_endpoint():
    """
    Simulates string execution on DFA or Minimized DFA (Phase 8).
    """
    try:
        data = request.get_json(silent=True) or {}
        input_string = data.get("input_string", "")
        pattern = data.get("pattern", "")
        automaton_type = data.get("automaton_type", "minimized")  # "dfa" or "minimized"
        include_dead_state = data.get("include_dead_state", True)

        if not pattern or not pattern.strip():
            return jsonify({
                "success": False,
                "error": "A regular expression pattern is required to simulate."
            }), 400

        nfa = build_nfa_from_regex(pattern.strip())
        dfa = nfa_to_dfa(nfa, include_dead_state=include_dead_state)

        if automaton_type == "minimized":
            target_dfa = minimize_dfa(dfa)
        else:
            target_dfa = dfa.to_dict()

        sim_result = simulate_dfa(target_dfa, input_string)

        return jsonify({
            "success": True,
            "pattern": pattern,
            "automaton_type": automaton_type,
            "automaton": target_dfa,
            "simulation": sim_result
        }), 200
    except RegexParseError as e:
        return jsonify({
            "success": False,
            "error": f"Syntax Error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Simulation Error: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Starting SENTINEL X Server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)

