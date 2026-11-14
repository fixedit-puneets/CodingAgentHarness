"""make check: run every test, print one line per test and a summary line."""
import sys
import unittest

sys.dont_write_bytecode = True


class Recorder(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.passed, self.failed = [], {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())

    def _bad(self, test, err):
        msg = " ".join(str(err[1]).split())[:140]
        self.failed[test.id()] = f"{err[0].__name__}: {msg}"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._bad(test, err)

    def addError(self, test, err):
        super().addError(test, err)
        self._bad(test, err)


suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
result = Recorder()
suite.run(result)
for tid in sorted(result.passed):
    print("PASS", tid)
for tid, msg in sorted(result.failed.items()):
    print("FAIL", tid, "|", msg)
total = len(result.passed) + len(result.failed)
print(f"Tests {len(result.passed)}/{total} passed")
sys.exit(0 if not result.failed else 1)
