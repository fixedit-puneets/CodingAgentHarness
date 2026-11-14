# Decisions (the WHY)

## Decision 1: plain functions in one module (calc.py), no classes
why: the app is tiny; plain functions keep the tests and the agent's job simple
rejected: a Calculator class - more code, nothing gained yet
cost: revisit if we ever add state such as memory or history

## Decision 2: division or modulo by zero raises ValueError
why: callers must never receive a silent None or inf
rejected: returning None (hides bugs), returning float("inf") (wrong for modulo)
cost: callers have to handle ValueError

## Decision 3: never use eval or exec to evaluate expressions
why: security - input like "__import__('os')" would execute
rejected: eval with restricted globals - still unsafe
cost: only the "a op b" form is supported for now (split into 3 tokens)
