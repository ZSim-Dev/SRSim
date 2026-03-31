## Code Style

- Use python3.10+ typing pattern, ex. Use str | None, rather than Optional[str], using builtin types as possible rather than typing module.
- Try not to `import whole-module`. Use `from module import func-or-Class`.
- Typing hint must pass the strict mode of static type checker.
- Not to use `from __future__ import annotations`, which is useless in python 3.14+

## Tech Stack

- This project is a simulator of `Honkai: Star Rail`, and will implement all mechanics of the game.
- Now we are developing the game core, and only use cli.
- This project are using python 3.14 free threaded build.


## Docs

- Read `docs/battle-system-mechanics.md` for battle system developing first, and read the detailed doc indexed.

## TODO Management

- Use GitHub issues as the default system for managing TODOs and planned work.
- Before creating a new TODO issue, review the relevant docs and current implementation first.
- Before creating a new issue, check existing open issues to avoid duplicates.
- If a topic is larger than one concrete task, create one tracking issue and split the work into linked sub-issues.
- Each TODO issue should have a clear scope, background, and expected outcome, so it can be picked up in a later session without extra context.
- When scope changes, or part of the work is finished, update the related GitHub issue instead of leaving the task only in chat context.
- Prefer GitHub issues over ad-hoc backlog notes in markdown files or source comments for cross-session task tracking.
- Use source-code TODO comments only for very local implementation notes that are directly tied to the current change.

## Reply

- 永远用简体中文回答用户
