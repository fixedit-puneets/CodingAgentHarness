# AGENTS.md - how a shift works

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
