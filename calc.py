def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b."""
    return a - b

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the quotient of a and b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Return the power of a and b."""
    return a ** b

def modulo(a, b):
    """Return the remainder of a and b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a % b

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
        return multiply(a, b)
    elif op == "/":
        return divide(a, b)
    elif op == "**":
        return power(a, b)
    elif op == "%":
        return modulo(a, b)

def calculate(expression):
    """Calculate the expression and return the result."""
    return parse_expression(expression)

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the quotient of a and b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Return the power of a and b."""
    return a ** b

def modulo(a, b):
    """Return the remainder of a and b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a % b

def calculate_expression(expression):
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
        return multiply(a, b)
    elif op == "/":
        return divide(a, b)
    elif op == "**":
        return power(a, b)
    elif op == "%":
        return modulo(a, b)

if __name__ == "__main__":
    import unittest
    class Calculator:
        def add(self, a, b):
            return add(a, b)

        def subtract(self, a, b):
            return subtract(a, b)

        def multiply(self, a, b):
            return multiply(a, b)

        def divide(self, a, b):
            return divide(a, b)

        def power(self, a, b):
            return power(a, b)

        def modulo(self, a, b):
            return modulo(a, b)

    calc = Calculator()
    unittest.main()

    def multiply(a, b):
        return a * b

    def divide(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(a, b):
        return a ** b

    def modulo(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a % b

    def calculate_expression(expression):
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
            return multiply(a, b)
        elif op == "/":
            return divide(a, b)
        elif op == "**":
            return power(a, b)
        elif op == "%":
            return modulo(a, b)

    def calculate(expression):
        return calculate_expression(expression)

    calc = Calculator()
    unittest.main()
