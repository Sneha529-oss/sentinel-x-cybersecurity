"""
SENTINEL X - Thompson's Construction NFA Generator
PRN: 202401110046

Constructs a Nondeterministic Finite Automaton (NFA) with ε-transitions
from a regular expression using Thompson's Construction algorithm.
"""

from backend.regex_parser import parse_regex_to_postfix, RegexParseError, EPSILON

class NFAFragment:
    """Represents an intermediate NFA fragment with single entry and exit states."""
    def __init__(self, start_state: int, accept_state: int):
        self.start_state = start_state
        self.accept_state = accept_state

class NFA:
    """Container for complete NFA structure and visualization formats."""
    def __init__(self, start_state: int, accept_states: set, states: set, transitions: dict, alphabet: set):
        self.start_state = start_state
        self.accept_states = accept_states
        self.states = states
        # transitions: dict of from_state -> dict of symbol -> set of to_states
        self.transitions = transitions
        self.alphabet = sorted(list(alphabet - {EPSILON}))

    def to_dict(self) -> dict:
        """Serializes NFA into a dictionary with transition tables and Cytoscape elements."""
        states_sorted = sorted(list(self.states))

        # Transition table representation
        columns = self.alphabet + [EPSILON]
        table_rows = []
        for s in states_sorted:
            is_start = (s == self.start_state)
            is_accept = (s in self.accept_states)
            prefix = ""
            if is_start and is_accept:
                prefix = "-> *"
            elif is_start:
                prefix = "->"
            elif is_accept:
                prefix = "*"

            row = {
                "state": f"q{s}",
                "raw_state": s,
                "prefix": prefix,
                "is_start": is_start,
                "is_accept": is_accept,
                "transitions": {}
            }
            for sym in columns:
                dest_states = sorted(list(self.transitions.get(s, {}).get(sym, set())))
                row["transitions"][sym] = [f"q{d}" for d in dest_states] if dest_states else []
            table_rows.append(row)

        # Cytoscape elements
        cy_nodes = []
        for s in states_sorted:
            classes = []
            if s == self.start_state:
                classes.append("start-node")
            if s in self.accept_states:
                classes.append("accept-node")
            if not classes:
                classes.append("normal-node")

            cy_nodes.append({
                "data": {
                    "id": f"q{s}",
                    "label": f"q{s}",
                    "raw_id": s,
                    "is_start": s == self.start_state,
                    "is_accept": s in self.accept_states
                },
                "classes": " ".join(classes)
            })

        cy_edges = []
        edge_counter = 0
        for src in states_sorted:
            for sym, dests in self.transitions.get(src, {}).items():
                for dst in sorted(list(dests)):
                    edge_counter += 1
                    is_eps = (sym == EPSILON)
                    cy_edges.append({
                        "data": {
                            "id": f"nfa_e_{edge_counter}",
                            "source": f"q{src}",
                            "target": f"q{dst}",
                            "label": sym,
                            "symbol": sym,
                            "is_epsilon": is_eps
                        },
                        "classes": "epsilon-edge" if is_eps else "symbol-edge"
                    })

        return {
            "type": "NFA",
            "start_state": f"q{self.start_state}",
            "raw_start_state": self.start_state,
            "accept_states": [f"q{s}" for s in sorted(list(self.accept_states))],
            "raw_accept_states": sorted(list(self.accept_states)),
            "states_count": len(self.states),
            "transitions_count": edge_counter,
            "alphabet": self.alphabet,
            "includes_epsilon": True,
            "table_columns": columns,
            "table_rows": table_rows,
            "cytoscape_elements": cy_nodes + cy_edges
        }

def build_nfa_from_regex(pattern: str) -> NFA:
    """
    Implements Thompson's Construction to compile a postfix regex into an NFA.
    """
    postfix_tokens = parse_regex_to_postfix(pattern)

    state_counter = 0

    def new_state() -> int:
        nonlocal state_counter
        s = state_counter
        state_counter += 1
        return s

    transitions = {} # from_state -> {symbol: set of to_states}
    alphabet = set()

    def add_trans(src: int, sym: str, dst: int):
        if src not in transitions:
            transitions[src] = {}
        if sym not in transitions[src]:
            transitions[src][sym] = set()
        transitions[src][sym].add(dst)
        if sym != EPSILON:
            alphabet.add(sym)

    frag_stack = []

    for token in postfix_tokens:
        ttype = token["type"]
        val = token["val"]

        if ttype == "SYMBOL":
            s0 = new_state()
            s1 = new_state()
            add_trans(s0, val, s1)
            frag_stack.append(NFAFragment(s0, s1))

        elif ttype == "CONCAT":
            if len(frag_stack) < 2:
                raise RegexParseError("Malformed expression: insufficient operands for concatenation.")
            frag2 = frag_stack.pop()
            frag1 = frag_stack.pop()
            add_trans(frag1.accept_state, EPSILON, frag2.start_state)
            frag_stack.append(NFAFragment(frag1.start_state, frag2.accept_state))

        elif ttype == "UNION":
            if len(frag_stack) < 2:
                raise RegexParseError("Malformed expression: insufficient operands for alternation.")
            frag2 = frag_stack.pop()
            frag1 = frag_stack.pop()
            s_new = new_state()
            a_new = new_state()
            add_trans(s_new, EPSILON, frag1.start_state)
            add_trans(s_new, EPSILON, frag2.start_state)
            add_trans(frag1.accept_state, EPSILON, a_new)
            add_trans(frag2.accept_state, EPSILON, a_new)
            frag_stack.append(NFAFragment(s_new, a_new))

        elif ttype == "QUANTIFIER":
            if not frag_stack:
                raise RegexParseError(f"Malformed expression: no operand for quantifier '{val}'.")
            frag = frag_stack.pop()
            s_new = new_state()
            a_new = new_state()

            if val == '*':
                # Kleene star
                add_trans(s_new, EPSILON, frag.start_state)
                add_trans(s_new, EPSILON, a_new)
                add_trans(frag.accept_state, EPSILON, frag.start_state)
                add_trans(frag.accept_state, EPSILON, a_new)
            elif val == '+':
                # 1 or more
                add_trans(s_new, EPSILON, frag.start_state)
                add_trans(frag.accept_state, EPSILON, frag.start_state)
                add_trans(frag.accept_state, EPSILON, a_new)
            elif val == '?':
                # Optional (0 or 1)
                add_trans(s_new, EPSILON, frag.start_state)
                add_trans(s_new, EPSILON, a_new)
                add_trans(frag.accept_state, EPSILON, a_new)

            frag_stack.append(NFAFragment(s_new, a_new))

    if len(frag_stack) != 1:
        raise RegexParseError("Malformed expression: unbalanced operators.")

    final_frag = frag_stack.pop()
    all_states = set(range(state_counter))

    return NFA(
        start_state=final_frag.start_state,
        accept_states={final_frag.accept_state},
        states=all_states,
        transitions=transitions,
        alphabet=alphabet
    )

