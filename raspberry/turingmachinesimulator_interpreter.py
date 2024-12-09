"""
This module contains the interpreter for the turingmachinesimulator syntax.
"""
from collections import defaultdict

import assets


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def parse_turing_machine(file_path):
    """Parses the Turing machine file, analyze the syntax and returns the machine configuration or
    errors."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    turing_machine = {
        "name": "",
        "init": "",
        "accept": set(),
        "state_transitions": defaultdict(dict),
        "errors": [],
        "warnings": []
    }

    string = ""

    # Parse the different sections
    line_number = 0
    for line in lines:
        line = line.strip()
        line_number += 1

        # Skip comments or empty lines
        if not line or line.startswith("//"):
            continue

        # Configuration section
        if line.startswith("name:"):
            turing_machine["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("init:"):
            turing_machine["init"] = line.split(":", 1)[1].strip()
        elif line.startswith("accept:"):
            accept_states = line.split(":", 1)[1].strip()
            turing_machine["accept"] = set(map(str.strip, accept_states.split(",")))



        # Delta-Function (Transitions)
        else:
            if string == "":
                string = line
                continue
            string = string + "," + line
            match = string.split(",")
            if len(match) != 5:
                turing_machine["errors"].append(f"Syntaxfehler (Zeile {line_number}): {string}")
                string = ""
                continue
            if match[1] not in assets.ALLOWED_SYMBOLS:
                turing_machine["errors"].append(
                    f"Symbol {match[1]} nicht erlaubt, bitte nutze {assets.ALLOWED_SYMBOLS} "
                    f"(Zeile {line_number}): {string}")
            match match[1]:
                case '0':
                    match[1] = assets.IO_BAND_COLORS(0)
                case '1':
                    match[1] = assets.IO_BAND_COLORS(1)
                case '_':
                    match[1] = assets.IO_BAND_COLORS(2)
            if match[3] not in assets.ALLOWED_SYMBOLS:
                turing_machine["errors"].append(
                    f"Symbol {match[3]} nicht erlaubt, bitte nutze {assets.ALLOWED_SYMBOLS} "
                    f"(Zeile {line_number}): {string}")
            match match[3]:
                case '0':
                    match[3] = assets.IO_BAND_COLORS(0)
                case '1':
                    match[3] = assets.IO_BAND_COLORS(1)
                case '_':
                    match[3] = assets.IO_BAND_COLORS(2)
            if match[4] not in ["<", ">", "-"]:
                turing_machine["errors"].append(
                    f"Operator {match[4]} nicht erlaubt (Zeile {line_number}): {string}")
            match match[4]:
                case "<":
                    match[4] = assets.ROBOT_DIRECTIONS.LEFT
                case ">":
                    match[4] = assets.ROBOT_DIRECTIONS.RIGHT
                case "-":
                    match[4] = assets.ROBOT_DIRECTIONS.HOLD
            if match:
                turing_machine["state_transitions"][(match[0], match[1])] = {
                    "new_state": match[2],
                    "write_symbol": match[3],
                    "move": match[4]
                }
            string = ""

    if turing_machine["name"] == "":
        turing_machine["errors"].append("Name der Turingmaschine fehlt.")
    if turing_machine["init"] == "":
        turing_machine["errors"].append("Initial Zustand fehlt.")
    if not turing_machine["accept"]:
        turing_machine["errors"].append("Akzeptierende Zustände fehlen.")
    if not turing_machine["state_transitions"]:
        turing_machine["errors"].append("Keine Transitionen angelegt.")

    if turing_machine["errors"]:
        turing_machine["errors"].append("Syntaxprüfung Fehlgeschlagen.")

    return semantic_analyzer(turing_machine)


def semantic_analyzer(turing_machine):
    """Analyzes the Programm for semantic errors."""
    transitions = turing_machine["state_transitions"]
    states = {key[0] for key in transitions.keys()}  # Alle definierten Zustände (match[0])
    new_states = {t["new_state"] for t in transitions.values()}  # Alle Folgezustände (match[2])

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

    return turing_machine
