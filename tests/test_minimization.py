"""
SENTINEL X - DFA Minimization & Simulator Tests
PRN: 202401110046
"""

import pytest
from backend.thompson_nfa import build_nfa_from_regex
from backend.subset_construction import nfa_to_dfa
from backend.dfa_minimization import minimize_dfa
from backend.simulator import simulate_dfa

def test_dfa_minimization_state_reduction():
    # Expression (a|b)*c produces an unminimized DFA with redundant states
    nfa = build_nfa_from_regex("(a|b)*c")
    dfa = nfa_to_dfa(nfa, include_dead_state=True)
    min_res = minimize_dfa(dfa)

    assert min_res["states_count"] <= len(dfa.states)
    assert min_res["states_reduced"] >= 0
    assert len(min_res["accept_states"]) > 0
    assert min_res["start_state"] is not None

def test_simulator_accept_trace():
    nfa = build_nfa_from_regex("(a|b)*c")
    dfa = nfa_to_dfa(nfa)
    min_res = minimize_dfa(dfa)

    sim = simulate_dfa(min_res, "abbac")
    assert sim["accepted"] is True
    assert sim["terminated_early"] is False
    assert sim["steps_count"] == 6  # Step 0 (START) + 5 character transitions
    assert "ACCEPTED" in sim["explanation"]

def test_simulator_reject_trace():
    nfa = build_nfa_from_regex("(a|b)*c")
    dfa = nfa_to_dfa(nfa)
    min_res = minimize_dfa(dfa)

    sim = simulate_dfa(min_res, "abba")
    assert sim["accepted"] is False
    assert "REJECTED" in sim["explanation"]

def test_simulator_unrecognized_symbol():
    nfa = build_nfa_from_regex("(a|b)*c")
    dfa = nfa_to_dfa(nfa)
    min_res = minimize_dfa(dfa)

    sim = simulate_dfa(min_res, "abz")
    assert sim["accepted"] is False
    assert sim["terminated_early"] is True
    assert "not in the automaton alphabet" in sim["explanation"]

def test_equivalence_of_dfa_and_minimized_dfa():
    nfa = build_nfa_from_regex("a(b|c)*")
    dfa = nfa_to_dfa(nfa)
    min_res = minimize_dfa(dfa)

    test_strings = ["a", "ab", "ac", "abbcccb", "b", "c", "aa"]
    for s in test_strings:
        sim_dfa = simulate_dfa(dfa.to_dict(), s)
        sim_min = simulate_dfa(min_res, s)
        assert sim_dfa["accepted"] == sim_min["accepted"], f"Discrepancy for string '{s}' between DFA and Minimized DFA"

