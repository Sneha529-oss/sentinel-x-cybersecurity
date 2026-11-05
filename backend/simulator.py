"""
SENTINEL X - Interactive DFA String Simulator
PRN: 202401110046

Executes an input string character-by-character on a DFA (or Minimized DFA),
recording the full deterministic state transition sequence, intermediate states,
and final acceptance or rejection verdict.
"""

def simulate_dfa(dfa_dict: dict, input_string: str) -> dict:
    """
    Simulates string execution on a DFA represented in serialized dictionary format.
    Works for both standard DFA and Minimized DFA dictionaries.
    """
    if not dfa_dict or "start_state" not in dfa_dict:
        return {
            "success": False,
            "error": "Invalid automaton configuration.",
            "accepted": False,
            "steps": []
        }

    start_state = dfa_dict["start_state"]
    accept_states = set(dfa_dict.get("accept_states", []))
    alphabet = set(dfa_dict.get("alphabet", []))
    dead_state = dfa_dict.get("dead_state")

    # Build transitions lookup
    # Can read from dfa_dict["transitions"] or from dfa_dict["table_rows"]
    transitions = {}
    if "transitions" in dfa_dict and isinstance(dfa_dict["transitions"], dict):
        transitions = dfa_dict["transitions"]
    elif "table_rows" in dfa_dict:
        for row in dfa_dict["table_rows"]:
            state = row["state"]
            transitions[state] = {}
            for sym, dest in row.get("transitions", {}).items():
                if dest and dest != "-":
                    transitions[state][sym] = dest

    curr_state = start_state
    steps = []
    step_num = 0

    # Initial state record before consuming characters
    steps.append({
        "step": step_num,
        "symbol": "START",
        "from_state": None,
        "to_state": curr_state,
        "is_accepting": curr_state in accept_states,
        "is_dead": curr_state == dead_state,
        "status": "INITIALIZED",
        "description": f"Initialized at start state {curr_state}."
    })

    string_chars = list(input_string) if input_string is not None else []
    terminated_early = False
    rejection_reason = ""

    for idx, char in enumerate(string_chars):
        step_num += 1

        if char not in alphabet:
            # Symbol not in alphabet
            terminated_early = True
            rejection_reason = f"Symbol '{char}' at position {idx} is not in the automaton alphabet Σ: {{{', '.join(sorted(alphabet))}}}."
            steps.append({
                "step": step_num,
                "symbol": char,
                "from_state": curr_state,
                "to_state": None,
                "is_accepting": False,
                "is_dead": True,
                "status": "UNRECOGNIZED_SYMBOL",
                "description": rejection_reason
            })
            break

        dest_state = transitions.get(curr_state, {}).get(char, None)

        if not dest_state or dest_state == "-":
            # Missing transition
            terminated_early = True
            rejection_reason = f"No defined transition δ({curr_state}, '{char}')."
            steps.append({
                "step": step_num,
                "symbol": char,
                "from_state": curr_state,
                "to_state": None,
                "is_accepting": False,
                "is_dead": True,
                "status": "NO_TRANSITION",
                "description": rejection_reason
            })
            break

        from_st = curr_state
        curr_state = dest_state
        is_acc = curr_state in accept_states
        is_dead = (curr_state == dead_state)

        desc = f"Read '{char}': Transition from {from_st} to {curr_state}."
        if is_dead:
            desc += " (Entered TRAP/DEAD state; string cannot be accepted)."

        steps.append({
            "step": step_num,
            "symbol": char,
            "from_state": from_st,
            "to_state": curr_state,
            "is_accepting": is_acc,
            "is_dead": is_dead,
            "status": "TRANSITION",
            "description": desc
        })

    is_accepted = (not terminated_early) and (curr_state in accept_states)

    verdict_explanation = ""
    if is_accepted:
        verdict_explanation = (
            f"ACCEPTED: Input '{input_string}' successfully consumed. "
            f"The DFA halted in state {curr_state}, which is an accepting (final) state."
        )
    else:
        if terminated_early:
            verdict_explanation = f"REJECTED: Execution aborted. {rejection_reason}"
        else:
            verdict_explanation = (
                f"REJECTED: Entire input was consumed, but the final state {curr_state} "
                f"is NOT an accepting state (Accepting states: {{{', '.join(sorted(accept_states))}}})."
            )

    return {
        "success": True,
        "input_string": input_string,
        "input_length": len(input_string),
        "start_state": start_state,
        "final_state": curr_state if not terminated_early else None,
        "accepted": is_accepted,
        "terminated_early": terminated_early,
        "explanation": verdict_explanation,
        "steps_count": len(steps),
        "steps": steps
    }

