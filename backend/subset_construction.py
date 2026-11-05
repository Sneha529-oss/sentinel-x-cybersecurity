"""
SENTINEL X - Subset Construction (NFA to DFA)
PRN: 202401110046

Converts a Nondeterministic Finite Automaton (NFA) to an equivalent
Deterministic Finite Automaton (DFA) using Subset Construction (Powerset Construction),
including ε-closure computation and dead/trap state handling.
"""

from collections import deque
from backend.thompson_nfa import NFA, EPSILON

class DFA:
    """Represents a Deterministic Finite Automaton."""
    def __init__(self, start_state: str, accept_states: set, states: list, transitions: dict, alphabet: list, dead_state: str = None, nfa_mapping: dict = None):
        self.start_state = start_state
        self.accept_states = accept_states
        self.states = states
        # transitions: {state_id: {symbol: dest_state_id}}
        self.transitions = transitions
        self.alphabet = alphabet
        self.dead_state = dead_state
        self.nfa_mapping = nfa_mapping or {}

    def to_dict(self) -> dict:
        """Serializes DFA into a dictionary with transition tables and Cytoscape elements."""
        table_rows = []
        for s in self.states:
            is_start = (s == self.start_state)
            is_accept = (s in self.accept_states)
            is_dead = (s == self.dead_state)

            prefix = ""
            if is_start and is_accept:
                prefix = "-> *"
            elif is_start:
                prefix = "->"
            elif is_accept:
                prefix = "*"

            nfa_subset = self.nfa_mapping.get(s, [])
            subset_label = "{" + ",".join(f"q{x}" for x in sorted(nfa_subset)) + "}" if nfa_subset else "∅ (Trap)"

            row = {
                "state": s,
                "label": f"{s}: {subset_label}",
                "prefix": prefix,
                "is_start": is_start,
                "is_accept": is_accept,
                "is_dead": is_dead,
                "nfa_states": sorted(list(nfa_subset)),
                "transitions": {}
            }
            for sym in self.alphabet:
                dest = self.transitions.get(s, {}).get(sym, None)
                row["transitions"][sym] = dest if dest else "-"
            table_rows.append(row)

        # Cytoscape elements
        cy_nodes = []
        for s in self.states:
            classes = []
            if s == self.start_state:
                classes.append("start-node")
            if s in self.accept_states:
                classes.append("accept-node")
            if s == self.dead_state:
                classes.append("dead-node")
            if not classes:
                classes.append("normal-node")

            nfa_subset = self.nfa_mapping.get(s, [])
            display_subset = "{" + ",".join(f"q{x}" for x in sorted(nfa_subset)) + "}" if nfa_subset else "TRAP"

            cy_nodes.append({
                "data": {
                    "id": s,
                    "label": f"{s}\n{display_subset}",
                    "short_label": s,
                    "is_start": s == self.start_state,
                    "is_accept": s in self.accept_states,
                    "is_dead": s == self.dead_state
                },
                "classes": " ".join(classes)
            })

        cy_edges = []
        edge_counter = 0
        for src in self.states:
            for sym in self.alphabet:
                dst = self.transitions.get(src, {}).get(sym)
                if dst:
                    edge_counter += 1
                    is_self_loop = (src == dst)
                    classes = "self-loop-edge" if is_self_loop else "dfa-edge"
                    if src == self.dead_state or dst == self.dead_state:
                        classes += " dead-edge"

                    cy_edges.append({
                        "data": {
                            "id": f"dfa_e_{edge_counter}",
                            "source": src,
                            "target": dst,
                            "label": sym,
                            "symbol": sym
                        },
                        "classes": classes
                    })

        return {
            "type": "DFA",
            "start_state": self.start_state,
            "accept_states": sorted(list(self.accept_states)),
            "states_count": len(self.states),
            "transitions_count": edge_counter,
            "alphabet": self.alphabet,
            "dead_state": self.dead_state,
            "has_dead_state": self.dead_state is not None,
            "table_columns": self.alphabet,
            "table_rows": table_rows,
            "cytoscape_elements": cy_nodes + cy_edges
        }

def compute_epsilon_closure(nfa: NFA, states: set) -> set:
    """Computes the ε-closure of a set of NFA states using BFS."""
    closure = set(states)
    queue = deque(states)

    while queue:
        curr = queue.popleft()
        eps_targets = nfa.transitions.get(curr, {}).get(EPSILON, set())
        for target in eps_targets:
            if target not in closure:
                closure.add(target)
                queue.append(target)

    return closure

def nfa_to_dfa(nfa: NFA, include_dead_state: bool = True) -> DFA:
    """
    Transforms an NFA into a DFA using Subset Construction.
    If include_dead_state is True, missing transitions map to a dedicated DEAD / trap state.
    """
    initial_closure = compute_epsilon_closure(nfa, {nfa.start_state})
    initial_key = frozenset(initial_closure)

    state_counter = 0
    dfa_mapping = {initial_key: f"D{state_counter}"}
    nfa_mapping = {f"D{state_counter}": sorted(list(initial_closure))}
    state_counter += 1

    unprocessed = deque([initial_key])
    dfa_transitions = {}
    dfa_states_order = [dfa_mapping[initial_key]]
    missing_transitions_found = False

    while unprocessed:
        curr_subset = unprocessed.popleft()
        curr_dfa_id = dfa_mapping[curr_subset]
        dfa_transitions[curr_dfa_id] = {}

        for sym in nfa.alphabet:
            # Compute move(curr_subset, sym)
            move_destinations = set()
            for nfa_state in curr_subset:
                dests = nfa.transitions.get(nfa_state, {}).get(sym, set())
                move_destinations.update(dests)

            if move_destinations:
                next_closure = compute_epsilon_closure(nfa, move_destinations)
                next_key = frozenset(next_closure)

                if next_key not in dfa_mapping:
                    next_dfa_id = f"D{state_counter}"
                    state_counter += 1
                    dfa_mapping[next_key] = next_dfa_id
                    nfa_mapping[next_dfa_id] = sorted(list(next_closure))
                    dfa_states_order.append(next_dfa_id)
                    unprocessed.append(next_key)

                dfa_transitions[curr_dfa_id][sym] = dfa_mapping[next_key]
            else:
                missing_transitions_found = True

    dead_state_id = None
    if include_dead_state and missing_transitions_found:
        dead_state_id = "DEAD"
        dfa_states_order.append(dead_state_id)
        dfa_transitions[dead_state_id] = {}
        nfa_mapping[dead_state_id] = []

        # Self loops for dead state
        for sym in nfa.alphabet:
            dfa_transitions[dead_state_id][sym] = dead_state_id

        # Fill missing transitions from other states to DEAD
        for s in dfa_states_order:
            if s == dead_state_id:
                continue
            for sym in nfa.alphabet:
                if sym not in dfa_transitions[s]:
                    dfa_transitions[s][sym] = dead_state_id

    # Identify accepting DFA states (contain at least one NFA accept state)
    accept_states = set()
    for subset_key, dfa_id in dfa_mapping.items():
        if any(s in nfa.accept_states for s in subset_key):
            accept_states.add(dfa_id)

    return DFA(
        start_state=dfa_mapping[initial_key],
        accept_states=accept_states,
        states=dfa_states_order,
        transitions=dfa_transitions,
        alphabet=nfa.alphabet,
        dead_state=dead_state_id,
        nfa_mapping=nfa_mapping
    )

