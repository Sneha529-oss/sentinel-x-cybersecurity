"""
SENTINEL X - Subset Construction (NFA to DFA) Tests
PRN: 202401110046
"""

import pytest
from backend.thompson_nfa import build_nfa_from_regex
from backend.subset_construction import nfa_to_dfa, compute_epsilon_closure

def test_epsilon_closure():
    nfa = build_nfa_from_regex("a|b")
    closure_start = compute_epsilon_closure(nfa, {nfa.start_state})
    # Start state of a|b branches via epsilon to starts of 'a' and 'b'
    assert len(closure_start) >= 3
    assert nfa.start_state in closure_start

def test_subset_construction_determinism():
    nfa = build_nfa_from_regex("(a|b)*c")
    dfa = nfa_to_dfa(nfa, include_dead_state=True)
    dfa_dict = dfa.to_dict()

    # In a DFA, for every state and symbol, there must be at most one destination
    for src, trans in dfa.transitions.items():
        for sym, dest in trans.items():
            assert isinstance(dest, str), f"DFA transition must be deterministic string state ID, got {type(dest)}"

    assert dfa_dict["dead_state"] == "DEAD"
    assert dfa_dict["has_dead_state"] is True
    assert len(dfa_dict["accept_states"]) > 0

def test_dfa_dead_state_self_loops():
    nfa = build_nfa_from_regex("ab")
    dfa = nfa_to_dfa(nfa, include_dead_state=True)
    dead = dfa.dead_state
    assert dead is not None

    # DEAD state must loop to itself on every alphabet symbol
    for sym in dfa.alphabet:
        assert dfa.transitions[dead][sym] == dead

