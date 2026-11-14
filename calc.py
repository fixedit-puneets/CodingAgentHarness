def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b."""
    return a - b

class Calculator:
    def __init__(self):
        pass

    def add(self, a, b):
        return add(a, b)

    def subtract(self, a, b):
        return subtract(a, b)

def parse_expression(expression):
    """Split the expression into tokens and call the corresponding function."""
    tokens = expression.split()
    if len(tokens) != 3:
        raise ValueError("Invalid expression")
    op = tokens[1]
    if op not in ["+", "-", "*", "/", "**", "%"]:
        raise ValueError("Invalid operator")
    a = int(tokens[0])
    b = int(tokens[2])
    if op == "+":
        return add(a, b)
    elif op == "-":
        return subtract(a, b)
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a // b
    elif op == "**":
        return a ** b
    elif op == "%":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a % b

def calculate(expression):
    """Calculate the expression and return the result."""
    return parse_expression(expression)

if __name__ == "__main__":
    import unittest
    unittest.main()
