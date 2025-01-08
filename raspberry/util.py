"""
The file contains Generally used things.
"""

import assets


# pylint: disable=too-many-branches
def semantic_analyzer(turing_machine):
    """
    Analyzes the turing_machine Programm for semantic errors.
    :param turing_machine:  the turing_machine programm
                            turing_machine = {
                                "name": "",
                                "init": "",
                                "accept": set(),
                                "state_transitions": defaultdict(dict),
                                "errors": [],
                                "warnings": []
                            }
    :return: the turing_machine programm with errors and warnings
    """
    transitions = turing_machine["state_transitions"]
    states = {key[0] for key in transitions.keys()}  # all defined states (match[0])
    new_states = {t["new_state"] for t in transitions.values()}  # all follow-states (match[2])

    # 1. Check if every combination of state and symbol exists
    for state in states:
        for symbol in assets.IO_BAND_COLORS:
            if (state, symbol) not in transitions:
                turing_machine["errors"].append(
                    f"Fehlende Transition für Zustand '{state}' mit Symbol '{symbol}'.")

    # 2. Initial and accepting states must be defined
    if turing_machine["init"] not in states:
        turing_machine["errors"].append(
            f"Initialzustand '{turing_machine['init']}' fehlt in den definierten Zuständen.")

    for accept_state in turing_machine["accept"]:
        if accept_state not in new_states:
            turing_machine["errors"].append(
                f"Akzeptier-Zustand '{accept_state}' ist nicht als Folgezustand definiert.")

    # 3. All next states must be defined (except if they are accepting states)
    for transition in transitions.values():
        next_state = transition["new_state"]
        if next_state not in states and next_state not in turing_machine["accept"]:
            turing_machine["warnings"].append(
                f"Folgezustand '{next_state}' ist weder definiert noch ein akzeptierender Zustand "
                f"und wird deshalb als nicht akzeptierender Zustand interpretiert.")

    # 4. No isolated states
    used_states = set(states)
    unique_next_states = set(new_states)
    for unique_next_state in unique_next_states:
        used_states.discard(unique_next_state)
    if turing_machine["init"] in used_states:
        used_states.discard(turing_machine["init"])
    if used_states:
        turing_machine["warnings"].append(
            f"Ungenutzte Zustände gefunden: {', '.join(used_states)}.")

    # 5. Check if accepting states have no outgoing transitions
    for accept_state in turing_machine["accept"]:
        if any(key[0] == accept_state for key in transitions.keys()):
            turing_machine["errors"].append(
                f"Akzeptier-Zustand '{accept_state}' hat ausgehende Transitionen.")

    for transition in transitions.keys():
        if transition[1] not in assets.IO_BAND_COLORS:
            turing_machine["errors"].append(
                f"Zeichen '{transition[1]}' ist nicht erlaubt")
    for transition in transitions.values():
        if transition["write_symbol"] not in assets.IO_BAND_COLORS:
            turing_machine["errors"].append(
                f"Zeichen '{transition["write_symbol"]}' ist nicht erlaubt. "
                f"Bitte verewende nur '0', '1', '_', ' '.")

    return turing_machine
