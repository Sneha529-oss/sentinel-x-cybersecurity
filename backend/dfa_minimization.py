"""
SENTINEL X - DFA Minimization Engine
PRN: 202401110046

Minimizes a Deterministic Finite Automaton (DFA) using Partition Refinement
(Hopcroft / Moore Equivalence Theorem). Eliminates equivalent and redundant states.
"""

from backend.subset_construction import DFA

def minimize_dfa(dfa: DFA) -> dict:
    """
    Minimizes a DFA using iterative partition refinement.
    Returns comparison metrics, transition tables, and Cytoscape elements for the minimized DFA.
    """
    states = dfa.states
    alphabet = dfa.alphabet
    accept_states = set(dfa.accept_states)
    non_accept_states = set(states) - accept_states

    # Initial partition P0: [Accepting, Non-Accepting]
    partition = []
    if accept_states:
        partition.append(sorted(list(accept_states)))
    if non_accept_states:
        partition.append(sorted(list(non_accept_states)))

    def get_group_index(state: str, current_partition: list) -> int:
        if state is None:
            return -1
        for idx, grp in enumerate(current_partition):
            if state in grp:
                return idx
        return -1

    # Iterative partition refinement
    changed = True
    iteration = 0
    while changed and iteration < 100:
        iteration += 1
        changed = False
        new_partition = []

        for group in partition:
            if len(group) <= 1:
                new_partition.append(group)
                continue

            # Split group according to transition signatures
            signature_map = {}
            for state in group:
                sig = []
                for sym in alphabet:
                    dest = dfa.transitions.get(state, {}).get(sym, None)
                    dest_group = get_group_index(dest, partition)
                    sig.append(dest_group)
                sig_tuple = tuple(sig)

                if sig_tuple not in signature_map:
                    signature_map[sig_tuple] = []
                signature_map[sig_tuple].append(state)

            if len(signature_map) > 1:
                changed = True
                for subgroup in signature_map.values():
                    new_partition.append(sorted(subgroup))
            else:
                new_partition.append(group)

        partition = new_partition

    # Re-order partition so group containing start_state is M0
    start_group_idx = get_group_index(dfa.start_state, partition)
    if start_group_idx != -1 and start_group_idx != 0:
        start_grp = partition.pop(start_group_idx)
        partition.insert(0, start_grp)

    # Assign IDs: M0, M1, M2...
    min_state_ids = []
    group_to_id = {}
    state_to_min_id = {}
    group_members_map = {}

    for idx, grp in enumerate(partition):
        min_id = f"M{idx}"
        # If group is solely the dead state, optionally tag as DEAD
        if dfa.dead_state and grp == [dfa.dead_state]:
            min_id = "M_DEAD"

        min_state_ids.append(min_id)
        group_to_id[tuple(grp)] = min_id
        group_members_map[min_id] = grp
        for s in grp:
            state_to_min_id[s] = min_id

    # Compute minimized transitions, start state, accept states
    min_start_state = state_to_min_id[dfa.start_state]
    min_accept_states = set()
    min_dead_state = state_to_min_id.get(dfa.dead_state) if dfa.dead_state else None
    min_transitions = {}

    for min_id in min_state_ids:
        min_transitions[min_id] = {}
        # Pick representative state from group
        rep_state = group_members_map[min_id][0]

        # Is this group accepting?
        if any(s in dfa.accept_states for s in group_members_map[min_id]):
            min_accept_states.add(min_id)

        for sym in alphabet:
            dest = dfa.transitions.get(rep_state, {}).get(sym, None)
            if dest and dest in state_to_min_id:
                min_transitions[min_id][sym] = state_to_min_id[dest]

    # Generate transition table rows
    table_rows = []
    for min_id in min_state_ids:
        is_start = (min_id == min_start_state)
        is_accept = (min_id in min_accept_states)
        is_dead = (min_id == min_dead_state)

        prefix = ""
        if is_start and is_accept:
            prefix = "-> *"
        elif is_start:
            prefix = "->"
        elif is_accept:
            prefix = "*"

        members = group_members_map[min_id]
        members_str = "{" + ",".join(members) + "}"

        row = {
            "state": min_id,
            "label": f"{min_id}: {members_str}",
            "prefix": prefix,
            "is_start": is_start,
            "is_accept": is_accept,
            "is_dead": is_dead,
            "equivalent_dfa_states": members,
            "transitions": {}
        }
        for sym in alphabet:
            dest = min_transitions.get(min_id, {}).get(sym, "-")
            row["transitions"][sym] = dest if dest else "-"
        table_rows.append(row)

    # Cytoscape elements
    cy_nodes = []
    for min_id in min_state_ids:
        classes = []
        if min_id == min_start_state:
            classes.append("start-node")
        if min_id in min_accept_states:
            classes.append("accept-node")
        if min_id == min_dead_state:
            classes.append("dead-node")
        if not classes:
            classes.append("normal-node")

        members = group_members_map[min_id]
        members_str = "{" + ",".join(members) + "}"

        cy_nodes.append({
            "data": {
                "id": min_id,
                "label": f"{min_id}\n{members_str}",
                "short_label": min_id,
                "is_start": min_id == min_start_state,
                "is_accept": min_id in min_accept_states,
                "is_dead": min_id == min_dead_state
            },
            "classes": " ".join(classes)
        })

    cy_edges = []
    edge_counter = 0
    for src in min_state_ids:
        for sym in alphabet:
            dst = min_transitions.get(src, {}).get(sym)
            if dst:
                edge_counter += 1
                is_self_loop = (src == dst)
                classes = "self-loop-edge" if is_self_loop else "dfa-edge"
                if src == min_dead_state or dst == min_dead_state:
                    classes += " dead-edge"

                cy_edges.append({
                    "data": {
                        "id": f"min_dfa_e_{edge_counter}",
                        "source": src,
                        "target": dst,
                        "label": sym,
                        "symbol": sym
                    },
                    "classes": classes
                })

    states_before = len(dfa.states)
    states_after = len(min_state_ids)
    states_reduced = states_before - states_after
    reduction_percentage = round((states_reduced / states_before) * 100, 1) if states_before > 0 else 0

    return {
        "type": "MINIMIZED_DFA",
        "start_state": min_start_state,
        "accept_states": sorted(list(min_accept_states)),
        "states": min_state_ids,
        "states_count": states_after,
        "states_before_count": states_before,
        "states_reduced": states_reduced,
        "reduction_percentage": reduction_percentage,
        "transitions_count": edge_counter,
        "alphabet": alphabet,
        "dead_state": min_dead_state,
        "transitions": min_transitions,
        "table_columns": alphabet,
        "table_rows": table_rows,
        "cytoscape_elements": cy_nodes + cy_edges,
        "partition_history": [f"Group {i}: {{{', '.join(g)}}}" for i, g in enumerate(partition)]
    }

