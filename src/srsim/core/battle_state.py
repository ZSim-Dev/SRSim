from dataclasses import dataclass, field
from typing import Any

from .actions import BaseAction, UltimateAction
from .enums import ActionType
from .events import EventBus, EventType
from .pending_actions import InsertedAction, InsertedActionKind, PendingActionQueue
from .timeline import Timeline
from .unit import Unit


@dataclass
class BattleState:
    allies: list[Unit]
    enemies: list[Unit]
    skill_points: int = 3
    max_skill_points: int = 5
    events: EventBus = field(init=False)
    timeline: Timeline = field(init=False)
    pending_actions: PendingActionQueue = field(init=False)
    turn_counter: int = 0
    battle_log: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.events = EventBus()
        self.timeline = Timeline(self.all_units())
        self.pending_actions = PendingActionQueue()

    def all_units(self) -> list[Unit]:
        return self.allies + self.enemies

    def alive_allies(self) -> list[Unit]:
        return [unit for unit in self.allies if not unit.is_defeated()]

    def alive_enemies(self) -> list[Unit]:
        return [unit for unit in self.enemies if not unit.is_defeated()]

    def is_finished(self) -> bool:
        return not self.alive_allies() or not self.alive_enemies()

    def add_log(self, entry: str) -> None:
        self.battle_log.append(entry)

    def adjust_skill_points(self, delta: int) -> None:
        self.skill_points = max(0, min(self.max_skill_points, self.skill_points + delta))

    def queue_ultimate(self, action: UltimateAction) -> None:
        if action.config.action_type != ActionType.ULTIMATE:
            raise ValueError("queue_ultimate requires an ultimate action")
        self.pending_actions.push(
            InsertedAction(
                kind=InsertedActionKind.ULTIMATE,
                actor=action.actor,
                action=action,
            )
        )
        self.events.emit(
            EventType.ULTIMATE_QUEUED,
            actor_id=action.actor.unit_id,
            payload={"action": action.config.name},
        )

    def queue_follow_up(self, action: BaseAction) -> None:
        self.pending_actions.push(
            InsertedAction(
                kind=InsertedActionKind.FOLLOW_UP,
                actor=action.actor,
                action=action,
            )
        )

    def grant_extra_turn(self, unit: Unit) -> None:
        self.pending_actions.push(
            InsertedAction(
                kind=InsertedActionKind.EXTRA_TURN,
                actor=unit,
            )
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "allies": [(unit.name, unit.hp, unit.shield, unit.energy) for unit in self.allies],
            "enemies": [(unit.name, unit.hp, unit.shield, unit.energy) for unit in self.enemies],
            "sp": self.skill_points,
        }
