## Code Style

- Use python3.10+ typing pattern, ex. Use str | None, rather than Optional[str], using builtin types as possible rather than typing module.
- Try not to `import whole-module`. Use `from module import func-or-Class`.
- Typing hint must pass the strict mode of static type checker.
- Not to use `from __future__ import annotations`, which is useless in python 3.14+

## Tech Stack

- This project is a simulator of `Honkai: Star Rail`, and will implement all mechanics of the game.
- Now we are developing the game core, and only use cli.
- This project are using python 3.14 free threaded build.

## Reply

- 永远用简体中文回答用户