"""
This module contains the interpreter for the turingmachine-program syntax.
"""
import re
import os
from collections import defaultdict

import assets
from assets import PROGRAM_LANGUAGES

import util


def parse_turing_machine(file_path, language: PROGRAM_LANGUAGES = PROGRAM_LANGUAGES.COM):
    """
    Parses a Turing machine file for different syntax styles.

    Args:
        file_path (str): Path to the Turing machine file.
        language (str): Language to parse ("com" (default) or "io").

    Returns:
        dict: Parsed Turing machine configuration and errors.
    """
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

    if language == PROGRAM_LANGUAGES.IO:
        # set tm-program name
        turing_machine["name"] = file_path.split(os.sep)[-1].split(".")[0]
        _parse_io_syntax(lines, turing_machine)
    elif language == PROGRAM_LANGUAGES.COM:
        _parse_com_syntax(lines, turing_machine)
    else:
        turing_machine["errors"].append(f"Unbekannte Sprache '{language}'.")

    # Validate the machine
    if turing_machine["init"] == "":
        turing_machine["errors"].append("Initial Zustand fehlt.")
    if not turing_machine["state_transitions"]:
        turing_machine["errors"].append("Keine Transitionen angelegt.")

    if turing_machine["errors"]:
        turing_machine["errors"].append("Syntaxprüfung Fehlgeschlagen.")

    return util.semantic_analyzer(turing_machine)


# pylint: disable=too-many-branches
def _parse_io_syntax(lines, turing_machine):
    """
    Parses the Turing machine in io syntax, allowing symbols in brackets and implicit state
    transitions.
    """
    table_started = False
    current_state = None

    for line in lines:
        # Remove comments
        line = line.split("#", 1)[0].strip()
        if not line:
            continue

        # Start state
        if line.startswith("start state:"):
            turing_machine["init"] = line.split(":", 1)[1].strip()
            continue

        # Accept states
        if line.startswith("accept states:"):
            accept_states = line.split(":", 1)[1].strip()
            turing_machine["accept"] = set(map(str.strip, accept_states.split(",")))
            continue

        # Transition table start
        if line.startswith("table:"):
            table_started = True
            continue

        # Process table
        if table_started:
            # State declaration
            if re.match(r"^\w+:$", line):
                current_state = line[:-1].strip()
                continue

            # Transition definition
            if current_state and ":" in line:
                symbol, instruction = map(str.strip, line.split(":", 1))

                # Handle multiple symbols inside brackets
                if symbol.startswith("[") and symbol.endswith("]"):
                    # Parse as a list of symbols, stripping whitespace and splitting on commas
                    symbols = [s.strip() for s in symbol[1:-1].split(",")]
                else:
                    # Treat as a single symbol
                    symbols = [symbol]

                for sym in symbols:
                    # Parse instruction
                    transition = _parse_io_instruction(instruction, current_state, sym)
                    if transition:
                        turing_machine["state_transitions"][
                            (current_state, _map_symbol(sym))] = transition
                    else:
                        turing_machine["errors"].append(f"Ungültige Anweisung: {line}")
            else:
                # Handle implicit state transitions like `R` or `L`
                if current_state and line in {"R", "L"}:
                    transition = {"move": line, "next": current_state}
                    turing_machine["state_transitions"][
                        (current_state, None)] = transition  # `None` represents any symbol
                else:
                    turing_machine["errors"].append(f"Ungültige Anweisung: {line}")


def _map_symbol(symbol: str):
    """
    Maps symbols in syntax to symbol Enum.

    Args:
        symbol (str): The symbol in io syntax.

    Returns:
        str: The mapped symbol.
    """

    symbol = symbol.strip("'")
    symbol = symbol.strip()

    match symbol:
        case "0":
            return assets.IO_BAND_COLORS.RED
        case "1":
            return assets.IO_BAND_COLORS.BLUE
        case "_" | '':
            return assets.IO_BAND_COLORS.BLANK
        case _:
            return symbol


def _map_direction(direction: str) -> assets.ROBOT_DIRECTIONS:
    match direction:
        case "<":
            return assets.ROBOT_DIRECTIONS.LEFT
        case ">":
            return assets.ROBOT_DIRECTIONS.RIGHT
        case "-":
            return assets.ROBOT_DIRECTIONS.HOLD
        case _:
            return assets.ROBOT_DIRECTIONS.HOLD


def _parse_io_instruction(instruction, current_state, symbol):
    """
    Parses a single transition instruction in io syntax.
    """
    move_map = {"L": "<", "R": ">"}

    # Simple move shorthand (e.g., "R", "L")
    if instruction in move_map:
        return {
            "new_state": current_state,  # Stay in the current state
            "write_symbol": _map_symbol(symbol),
            "move": move_map[instruction]
        }

    # Full instruction (e.g., "{write: 0, L: carry}")
    if instruction.startswith("{") and instruction.endswith("}"):
        instruction = instruction[1:-1].strip()  # Remove braces
        parts = instruction.split(",")

        # Create a dictionary from the instruction,
        # but handle cases where a part doesn't contain ":"
        parsed_parts = {}
        for part in parts:
            key_value = part.strip().split(":", 1)
            if len(key_value) == 2:
                parsed_parts[key_value[0].strip()] = key_value[1].strip()
            elif len(key_value) == 1:
                # If we have only one value (e.g., "L"),
                # assume it's a state transition to the current state
                if key_value[0].strip() in move_map:
                    parsed_parts[key_value[0].strip()] = current_state
                else:
                    # Handle unexpected format or invalid instruction
                    return None

        # Ensure the new state is properly set
        new_state = parsed_parts.get("L", parsed_parts.get("R", current_state)).strip()

        # Handle move direction (L or R) and the symbol to write
        move = move_map.get("L", "<") if "L" in parsed_parts else move_map.get("R", ">")
        write_symbol = _map_symbol(parsed_parts.get("write", symbol))

        return {
            "new_state": new_state,
            "write_symbol": write_symbol,
            "move": _map_direction(move)
        }

    return None


def _parse_com_syntax(lines, turing_machine):
    """
    Parses the Turing machine in com syntax.
    """
    string = ""
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

        # Transition section
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
            turing_machine["state_transitions"][(match[0], _map_symbol(match[1]))] = {
                "new_state": match[2],
                "write_symbol": _map_symbol(match[3]),
                "move": _map_direction(match[4])
            }
            string = ""
