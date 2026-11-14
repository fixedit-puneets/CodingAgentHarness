import importlib
import re
import unittest
from pathlib import Path


def calc():
    # imported inside each test so one broken calc.py is counted per test, not as 1 big error
    return importlib.import_module("calc")


class Test_add_subtract(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calc().add(2, 3), 5)

    def test_add_negative(self):
        self.assertEqual(calc().add(-2, 3), 1)

    def test_subtract(self):
        self.assertEqual(calc().subtract(10, 4), 6)

    def test_subtract_negative_result(self):
        self.assertEqual(calc().subtract(2, 5), -3)


class Test_multiply_divide(unittest.TestCase):
    def test_multiply(self):
        self.assertEqual(calc().multiply(6, 7), 42)

    def test_multiply_by_zero(self):
        self.assertEqual(calc().multiply(5, 0), 0)

    def test_divide(self):
        self.assertEqual(calc().divide(10, 4), 2.5)

    def test_divide_by_zero_raises_value_error(self):  # decision 2
        with self.assertRaises(ValueError):
            calc().divide(1, 0)


class Test_power_modulo(unittest.TestCase):
    def test_power(self):
        self.assertEqual(calc().power(2, 10), 1024)

    def test_power_negative_exponent(self):
        self.assertEqual(calc().power(2, -1), 0.5)

    def test_modulo(self):
        self.assertEqual(calc().modulo(7, 3), 1)

    def test_modulo_by_zero_raises_value_error(self):  # decision 2
        with self.assertRaises(ValueError):
            calc().modulo(7, 0)


class Test_parse_expression(unittest.TestCase):
    def test_add(self):
        self.assertEqual(calc().calculate("2 + 3"), 5)

    def test_divide(self):
        self.assertEqual(calc().calculate("10 / 4"), 2.5)

    def test_power(self):
        self.assertEqual(calc().calculate("2 ** 10"), 1024)

    def test_modulo(self):
        self.assertEqual(calc().calculate("7 % 3"), 1)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            calc().calculate("1 / 0")

    def test_garbage_input(self):
        with self.assertRaises(ValueError):
            calc().calculate("two plus three")


class Test_policy(unittest.TestCase):
    """Decision 3 enforced mechanically: a decision nobody checks is just a wish."""

    def test_no_eval_or_exec(self):
        src = Path("calc.py").read_text()
        self.assertIsNone(re.search(r"\b(eval|exec)\s*\(", src), "calc.py must not call eval/exec")
