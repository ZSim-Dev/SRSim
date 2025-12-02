import heapq
from dataclasses import dataclass, field
from itertools import count
from typing import Any

_counter = count()


@dataclass(order=True)
class QueuedAction:
    priority: int
    order: int = field(init=False)
    action: Any = field(compare=False)

    def __post_init__(self) -> None:
        self.order = next(_counter)


class PendingActionQueue:
    def __init__(self) -> None:
        self._queue: list[QueuedAction] = []

    def push(self, action: Any, priority: int) -> None:
        heapq.heappush(self._queue, QueuedAction(-priority, action=action))

    def pop(self) -> Any | None:
        if not self._queue:
            return None
        queued = heapq.heappop(self._queue)
        return queued.action

    def __len__(self) -> int:
        return len(self._queue)
