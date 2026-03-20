from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    BATTLE_START = "battle_start"
    WAVE_START = "wave_start"
    TURN_START = "turn_start"
    ACTION_START = "action_start"
    HIT = "hit"
    DAMAGE_DEALT = "damage_dealt"
    HEAL_DONE = "heal_done"
    SHIELD_APPLIED = "shield_applied"
    TOUGHNESS_DAMAGE = "toughness_damage"
    WEAKNESS_BREAK = "weakness_break"
    STATUS_APPLY = "status_apply"
    STATUS_EXPIRE = "status_expire"
    KILL = "kill"
    UNIT_DOWNED = "unit_downed"
    ACTION_END = "action_end"
    TURN_END = "turn_end"


@dataclass
class BattleEvent:
    event_type: EventType
    actor_id: str | None = None
    target_id: str | None = None
    payload: dict[str, str | int | float | bool] = field(default_factory=dict)


EventHandler = Callable[[BattleEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[EventHandler]] = {event: [] for event in EventType}
        self.history: list[BattleEvent] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._subscribers[event_type].append(handler)

    def emit(
        self,
        event_type: EventType,
        *,
        actor_id: str | None = None,
        target_id: str | None = None,
        payload: dict[str, str | int | float | bool] | None = None,
    ) -> BattleEvent:
        event = BattleEvent(
            event_type=event_type,
            actor_id=actor_id,
            target_id=target_id,
            payload=payload or {},
        )
        self.history.append(event)
        for handler in self._subscribers[event_type]:
            handler(event)
        return event
