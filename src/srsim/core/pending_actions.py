import heapq
from dataclasses import dataclass, field
from enum import IntEnum
from itertools import count
from typing import TYPE_CHECKING

_counter = count()

if TYPE_CHECKING:
    from .actions import BaseAction
    from .unit import Unit


class InsertedActionKind(IntEnum):
    ULTIMATE = 0
    EXTRA_TURN = 1
    FOLLOW_UP = 2


@dataclass(frozen=True)
class InsertedAction:
    kind: InsertedActionKind
    actor: "Unit"
    action: "BaseAction | None" = None


@dataclass(order=True)
class QueuedAction:
    priority: InsertedActionKind
    order: int = field(init=False)
    inserted_action: InsertedAction = field(compare=False)

    def __post_init__(self) -> None:
        self.order = next(_counter)


class PendingActionQueue:
    def __init__(self) -> None:
        self._queue: list[QueuedAction] = []

    def push(self, inserted_action: InsertedAction) -> None:
        heapq.heappush(
            self._queue,
            QueuedAction(priority=inserted_action.kind, inserted_action=inserted_action),
        )

    def pop(self) -> InsertedAction | None:
        if not self._queue:
            return None
        queued = heapq.heappop(self._queue)
        return queued.inserted_action

    def __len__(self) -> int:
        return len(self._queue)
