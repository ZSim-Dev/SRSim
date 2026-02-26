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

## Cursor Cloud specific instructions

- **运行时**: 项目使用 Python 3.14 free-threaded build (`3.14t`)，通过 `uv python install 3.14t` 安装。`.python-version` 文件指定了 `3.14t`，`uv` 会自动识别。
- **包管理器**: 仅使用 `uv`。依赖刷新命令为 `uv sync`。
- **常用命令**:
  - 运行测试: `uv run pytest -v`
  - 运行 lint: `uv run ruff check src/ tests/`
  - 格式化检查: `uv run ruff format --check src/ tests/`
  - 运行 demo 战斗: `uv run python src/main.py`
- **无外部服务依赖**: 本项目为纯 Python CLI 模拟器，无需数据库、Docker 或其他外部服务。
- **PATH 注意事项**: `uv` 安装在 `$HOME/.local/bin`，确保该路径在 `PATH` 中（更新脚本已处理）。