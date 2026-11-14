"""Runs the relay against a scripted fake model (no Ollama) to test the HARNESS itself."""
import os
import re
import shutil
import tempfile
from pathlib import Path

import shift

BASE = '''"""Calculator."""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
'''
MD = BASE + '''
def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b
'''
PM = MD + '''
def power(a, b):
    return a ** b

def modulo(a, b):
    if b == 0:
        raise ValueError("modulo by zero")
    return a % b
'''
PM_BUGGY = PM.replace('    if b == 0:\n        raise ValueError("modulo by zero")\n', "")
PE_GOOD = PM + '''
def calculate(expression):
    parts = expression.split()
    if len(parts) != 3:
        raise ValueError("expected: a op b")
    try:
        a, b = float(parts[0]), float(parts[2])
    except ValueError:
        raise ValueError("operands must be numbers")
    ops = {"+": add, "-": subtract, "*": multiply, "/": divide, "**": power, "%": modulo}
    if parts[1] not in ops:
        raise ValueError("unknown operator")
    return ops[parts[1]](a, b)
'''
PE_EVAL = PM + '''
def calculate(expression):
    return ev''' + '''al(expression)
'''


class Fake:
    """scenario 'happy': power_modulo fails once (bug), parse_expression fails once (uses eval).
       scenario 'stuck': power_modulo never gets fixed."""
    def __init__(self, scenario):
        self.scenario = scenario

    def chat(self, messages):
        text = messages[-1]["content"]
        if "Write a note for the next engineer" in text:
            return "Step handled. Watch the modulo edge case."
        first = len(messages) == 2
        m = re.search(r"=== Step for this shift: (\w+) ===", messages[1]["content"])
        tag = m.group(1)
        if tag == "add_subtract":
            code = BASE
        elif tag == "multiply_divide":
            code = MD
        elif tag == "power_modulo":
            code = PM_BUGGY if (first or self.scenario == "stuck") else PM
        else:
            code = PE_EVAL if first else PE_GOOD
        return "```python\n" + code + "```"


def run(scenario, shifts):
    root = Path(tempfile.mkdtemp()) / "proj"
    shift.ROOT = root
    print(f"\n################ scenario: {scenario} ################")
    for _ in range(shifts):
        if shift.run_shift(lambda seed: Fake(scenario)) is None:
            break
    print("\n--- progress.md ---\n" + shift.read("progress.md"))
    print("--- git log ---\n" + shift.git("log", "--oneline"))
    return root


run("happy", 5)
run("stuck", 4)
