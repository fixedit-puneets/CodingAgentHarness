"""Repo as the system of record - shift-based agents building a calculator.

Each shift is a FRESH agent (new Ollama client, empty context). It knows nothing except
what it reads from the repo: AGENTS.md, progress.md, decisions.md, the code and the tests.

    python shift.py --shifts 4     # run up to 4 shifts (one per roadmap step)
    python shift.py                # run exactly one shift
    python shift.py --status       # show progress.md and git log
    python shift.py --reset        # restore calc.py and progress.md in this repo

Commits land in this repository (the one that tracks origin) and are pushed
to origin. This script does not create a second git repo.

"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MODEL_NAME = "llama3.2:3b"
# This checkout. CALC_ROOT is only for the offline selftest, which uses a temp directory.
ROOT = Path(os.environ.get("CALC_ROOT", Path(__file__).resolve().parent))
MAX_ATTEMPTS = 3

# =====================================================================================
# Files that make up the project's memory and definition of done (written once)
# =====================================================================================
AGENTS_MD = r'''# AGENTS.md - how a shift works

You are one agent in a relay. The agent before you is gone and the agent after you has
never seen this conversation. This repo is the only memory.

## Clock in
1. Read progress.md   (where are we?)
2. Read decisions.md  (why is it built this way? do not undo decisions)
3. Run `make check`   (what is the real test status?)
4. Continue from the FIRST item under "Next steps". Only that one.

## While working
- Edit only calc.py. Never edit anything in tests/ - the tests are the definition of done.
- Keep every function that already exists.
- Never use eval or exec to evaluate expressions (see decision 3).

## Clock out
1. Run `make check` again.
2. Update progress.md (state, completed, in progress, known issues, next steps, a short note).
3. Commit: the code first, then progress.md.
'''

DECISIONS_MD = r'''# Decisions (the WHY)

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
'''

MAKEFILE = 'PYTHON ?= python3\n\ncheck:\n\t"$(PYTHON)" check.py\n'

CHECK_PY = r'''"""make check: run every test, print one line per test and a summary line."""
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
'''

CALC_STUB = '"""Calculator. Built step by step by shift agents."""\n'

TESTS_PY = r'''import importlib
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
'''

# =====================================================================================
# Small helpers: git, make check, progress.md parsing/rendering
# =====================================================================================
def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout.strip()


def commit(paths, title, body=""):
    """Stage `paths`, commit only if something changed, return the short HEAD hash."""
    git("add", *paths)
    scope = [] if paths == ["-A"] else ["--", *paths]
    if git("status", "--porcelain", *scope):
        cmd = ["commit", "-q", "-m", title] + (["-m", body] if body else [])
        git(*cmd)
    return git("rev-parse", "--short", "HEAD")


def push_origin():
    """Push HEAD to the CodingAgentHarness remote. Skip when this checkout has no origin."""
    if "origin" not in git("remote").split():
        return
    print("  git push origin HEAD")
    git("push", "-u", "origin", "HEAD")


def run_check():
    """`make check` (falls back to python check.py when make is not installed)."""
    if shutil.which("make"):
        cmd = ["make", "-s", "check", f"PYTHON={sys.executable}"]
    else:
        cmd = [sys.executable, "check.py"]
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=60)
        raw = out.stdout + out.stderr
    except subprocess.TimeoutExpired:
        return {"passed": set(), "failed": {"check.timeout": "make check timed out (infinite loop?)"},
                "total": 1, "raw": "timeout"}
    passed = {l.split()[1] for l in raw.splitlines() if l.startswith("PASS ")}
    failed = {}
    for l in raw.splitlines():
        if l.startswith("FAIL "):
            tid, _, msg = l[5:].partition(" | ")
            failed[tid] = msg
    return {"passed": passed, "failed": failed, "total": len(passed) + len(failed), "raw": raw}


def step_stats(res, tag):
    mark = f".Test_{tag}."
    ok = sum(mark in t for t in res["passed"])
    bad = {t: m for t, m in res["failed"].items() if mark in t}
    return ok, ok + len(bad), bad


def parse_progress(text):
    sections, cur = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            sections[cur] = []
        elif cur and line.strip():
            sections[cur].append(line.strip())
    return sections


def items(sections, name):
    return [l[2:] for l in sections.get(name, []) if l.startswith("- ") and l != "- (none)"]


def kv(sections, key, default=""):
    for l in sections.get("Current state", []):
        if l.startswith(key + ":"):
            return l.split(":", 1)[1].strip()
    return default


def render_progress(s):
    def block(title, lines):
        return [f"## {title}", *(lines or ["- (none)"]), ""]

    out = ["# Progress", "", "## Current state",
           f"commit: {s['commit']}", f"tests: {s['passed']}/{s['total']} passed",
           f"shift: {s['shift']}", ""]
    out += block("Completed", [f"- {x}" for x in s["completed"]])
    out += block("In progress", [f"- {x}" for x in s["in_progress"]])
    out += block("Known issues", [f"- {x}" for x in s["issues"]])
    out += block("Next steps", [f"- {x}" for x in s["next"]])
    out += ["## Notes for next shift", s["note"] or "(none)", ""]
    return "\n".join(out)


def read(rel):
    return (ROOT / rel).read_text()


# =====================================================================================
# Bootstrap (idempotent) - writes missing project files into the current repo
# =====================================================================================
ROADMAP = [
    "add_subtract: add(a, b) and subtract(a, b)",
    "multiply_divide: multiply(a, b) and divide(a, b)",
    "power_modulo: power(a, b) and modulo(a, b)",
    'parse_expression: calculate("2 + 3") splits "a op b" into 3 tokens (ops + - * / ** %) '
    "and calls the functions above",
]


def bootstrap():
    ROOT.mkdir(parents=True, exist_ok=True)
    files = {"AGENTS.md": AGENTS_MD, "decisions.md": DECISIONS_MD, "Makefile": MAKEFILE,
             "check.py": CHECK_PY, "calc.py": CALC_STUB, ".gitignore": "__pycache__/\n*.pyc\n",
             "tests/__init__.py": "", "tests/test_calc.py": TESTS_PY}
    created = []
    for rel, text in files.items():
        p = ROOT / rel
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
            created.append(rel)
    if not (ROOT / "progress.md").exists():
        res = run_check()
        (ROOT / "progress.md").write_text(render_progress({
            "commit": "(none yet)", "passed": len(res["passed"]), "total": res["total"], "shift": 0,
            "completed": [], "in_progress": [], "issues": [], "next": ROADMAP, "note": ""}))
        created.append("progress.md")
    if (ROOT / ".git").exists():
        if created:
            commit(created, "add calculator files to this repo")
            push_origin()
        return
    # Offline selftest only. The CodingAgentHarness checkout already has .git and origin.
    git("init", "-q")
    git("config", "user.name", "shift-harness")
    git("config", "user.email", "shift@example.local")
    commit(["-A"], "init: skeleton, tests, rules, decisions, progress")


# =====================================================================================
# The model. A new client per shift = a brand new agent with an empty context window.
# =====================================================================================
class OllamaClient:
    def __init__(self, seed=1):
        import ollama

        self._ollama, self.seed = ollama, seed

    def chat(self, messages):
        r = self._ollama.chat(model=MODEL_NAME, messages=messages,
                              options={"seed": self.seed, "temperature": 0.2, "num_ctx": 4096})
        return r["message"]["content"]


def extract_code(text):
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip() + "\n"


SYSTEM = (
    "You are a coding agent working ONE shift in a relay on a small Python calculator. "
    "The repository files shown to you are your ONLY memory. "
    "Reply with the COMPLETE new contents of calc.py in ONE ```python code block and nothing else."
)


def build_task(tag, desc, tests_src):
    return "\n".join([
        "=== AGENTS.md ===", read("AGENTS.md"),
        "=== decisions.md ===", read("decisions.md"),
        "=== progress.md ===", read("progress.md"),
        "=== current calc.py ===", read("calc.py"),
        "=== tests you must make pass (never edit them) ===", tests_src,
        f"=== Step for this shift: {tag} ===", desc,
        "Keep all existing functions. Follow decisions.md. Do not write the words eval or exec.",
    ])


def test_source_for(tag):
    src = read("tests/test_calc.py")
    m = re.search(rf"class Test_{tag}\b.*?(?=\nclass |\Z)", src, re.S)
    return m.group(0) if m else ""


def handoff_note(client, tag, ok, attempts, summary, failures):
    facts = (f"Step: {tag}. Result: {'passed' if ok else 'FAILED'} after {attempts} attempt(s). "
             f"{summary}. " + (f"Failing tests: {'; '.join(failures)}." if failures else ""))
    try:
        text = client.chat([{"role": "user", "content":
            "Write a note for the next engineer in at most 2 short sentences: what happened this "
            "shift and one thing to watch. Use ONLY these facts, invent nothing:\n" + facts}])
    except Exception:
        text = ""
    text = " ".join(text.split())[:300]
    return text if len(text) > 5 else facts


# =====================================================================================
# One shift: clock in -> work -> clock out
# =====================================================================================
def run_shift(make_client):
    bootstrap()
    sections = parse_progress(read("progress.md"))
    todo = items(sections, "Next steps")
    if not todo:
        print("Nothing left in 'Next steps' - the project is complete.")
        return None
    shift_no = int(kv(sections, "shift", "0") or 0) + 1
    client = make_client(shift_no)                      # fresh agent, fresh context
    print(f"\n=================== SHIFT {shift_no}: fresh agent, empty context ===================")

    # ---------------------------------- CLOCK IN ----------------------------------
    print("CLOCK IN")
    print("  read AGENTS.md, progress.md, decisions.md")
    baseline = run_check()
    print(f"  make check -> Tests {len(baseline['passed'])}/{baseline['total']} passed")
    step = todo[0]
    tag, _, desc = step.partition(": ")
    tests_src = test_source_for(tag)
    if not tests_src:
        sys.exit(f"No tests named Test_{tag} - the roadmap and the tests disagree.")
    print(f"  next step (first item under 'Next steps'): {tag}")
    for issue in items(sections, "Known issues"):
        print(f"  known issue from a previous shift: {issue[:90]}")

    # ----------------------------------- WORK -------------------------------------
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": build_task(tag, desc, tests_src)}]
    saved_calc = read("calc.py") if (ROOT / "calc.py").exists() else CALC_STUB
    ok, attempts, res, failing = False, 0, baseline, {}
    for attempts in range(1, MAX_ATTEMPTS + 1):
        reply = client.chat(messages)
        (ROOT / "calc.py").write_text(extract_code(reply))          # the ONLY file the agent writes
        res = run_check()
        n_ok, n_all, failing = step_stats(res, tag)
        broken = sorted(baseline["passed"] - res["passed"])         # regression guard
        ok = n_all > 0 and not failing and not broken
        print(f"  attempt {attempts}: step tests {n_ok}/{n_all}"
              + (f", REGRESSIONS: {[b.split('.')[-1] for b in broken]}" if broken else ""))
        if ok:
            break
        feedback = [f"- {t.split('.')[-1]}: {m}" for t, m in failing.items()]
        feedback += [f"- previously passing test now broken: {b.split('.')[-1]}" for b in broken]
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": "make check failed:\n" + "\n".join(feedback)
                      + "\nFix it. Reply with the complete calc.py in ONE ```python block."}]

    # ---------------------------------- CLOCK OUT ---------------------------------
    print("CLOCK OUT")
    pct = round(100 * step_stats(res, tag)[0] / max(step_stats(res, tag)[1], 1))
    if ok:
        commit(["calc.py"], f"shift {shift_no}: {tag} done", f"Why: roadmap step '{desc}'. "
               f"Tests {len(res['passed'])}/{res['total']} passed.")
    else:
        (ROOT / "calc.py").write_text(saved_calc)                   # keep the last good calc.py
        print("  step NOT finished -> calc.py rolled back so the repo stays green")
    final = run_check()                                             # 'run make check' at clock out
    print(f"  make check -> Tests {len(final['passed'])}/{final['total']} passed")

    state = {"completed": items(sections, "Completed"), "in_progress": [], "next": todo,
             "issues": [i for i in items(sections, "Known issues") if not i.startswith(tag + ":")]}
    if ok:
        state["completed"].append(step)
        state["next"] = todo[1:]
    else:
        state["in_progress"] = [f"{tag} [{pct}%]"]
        state["issues"] += [f"{tag}: {t.split('.')[-1]} - {m}" for t, m in failing.items()]

    summary = f"Tests {len(final['passed'])}/{final['total']} passed"
    state["note"] = handoff_note(client, tag, ok, attempts, summary,
                                 [t.split(".")[-1] for t in failing])
    head = git("rev-parse", "--short", "HEAD")
    state.update(commit=head, passed=len(final["passed"]), total=final["total"], shift=shift_no)
    (ROOT / "progress.md").write_text(render_progress(state))
    commit(["progress.md"], f"shift {shift_no}: progress.md - {tag} {'done' if ok else 'blocked'}")
    print("  updated progress.md and committed (code first, progress second)")
    push_origin()
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shifts", type=int, default=1)
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    if args.reset:
        # Never delete this checkout. A separate CALC_ROOT (selftest) can be removed.
        if ROOT.resolve() == Path(__file__).resolve().parent:
            for rel in ("calc.py", "progress.md"):
                p = ROOT / rel
                if p.exists():
                    p.unlink()
        elif ROOT.exists():
            shutil.rmtree(ROOT)
    bootstrap()
    if args.status:
        print(read("progress.md"))
    else:
        for _ in range(args.shifts):
            if run_shift(lambda seed: OllamaClient(seed)) is None:
                break
    print("\n--- git log ---")
    print(git("log", "--oneline"))


if __name__ == "__main__":
    main()
