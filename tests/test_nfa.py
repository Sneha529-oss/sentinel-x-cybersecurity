"""
SENTINEL X - Thompson's Construction NFA Tests
PRN: 202401110046
"""

import pytest
from backend.regex_parser import infix_to_postfix, tokenize_and_insert_concat, RegexParseError
from backend.thompson_nfa import build_nfa_from_regex, EPSILON

def test_tokenizer_and_concat():
    tokens = tokenize_and_insert_concat("ab")
    vals = [t["val"] for t in tokens]
    assert vals == ["a", "·", "b"]

def test_shunting_yard_precedence():
    postfix = infix_to_postfix("(a|b)*c")
    vals = [t["val"] for t in postfix]
    assert vals == ["a", "b", "|", "*", "c", "·"]

def test_unbalanced_parentheses_error():
    with pytest.raises(RegexParseError):
        infix_to_postfix("(a|b")

def test_single_symbol_nfa():
    nfa = build_nfa_from_regex("a")
    nfa_dict = nfa.to_dict()
    assert nfa_dict["states_count"] == 2
    assert nfa_dict["alphabet"] == ["a"]
    assert nfa.transitions[nfa.start_state]["a"] == {list(nfa.accept_states)[0]}

def test_concatenation_nfa():
    nfa = build_nfa_from_regex("ab")
    nfa_dict = nfa.to_dict()
    assert nfa_dict["states_count"] == 4
    assert set(nfa_dict["alphabet"]) == {"a", "b"}

def test_alternation_nfa():
    nfa = build_nfa_from_regex("a|b")
    nfa_dict = nfa.to_dict()
    # Alternation adds 2 wrapper states (start + accept) around two 2-state fragments = 6 states
    assert nfa_dict["states_count"] == 6
    assert set(nfa_dict["alphabet"]) == {"a", "b"}

def test_kleene_star_nfa():
    nfa = build_nfa_from_regex("a*")
    nfa_dict = nfa.to_dict()
    # Star adds 2 wrapper states around a 2-state fragment = 4 states
    assert nfa_dict["states_count"] == 4
    assert nfa_dict["alphabet"] == ["a"]

def test_complex_nfa_properties():
    nfa = build_nfa_from_regex("(a|b)*c")
    nfa_dict = nfa.to_dict()
    assert nfa_dict["states_count"] == 10
    assert set(nfa_dict["alphabet"]) == {"a", "b", "c"}
    assert nfa_dict["transitions_count"] > 0
    assert len(nfa_dict["cytoscape_elements"]) > 0

