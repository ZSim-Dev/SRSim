from dataclasses import dataclass

from .actions import BaseAction, UltimateAction
from .ai import SimpleAI
from .battle_state import BattleState
from .events import EventType
from .enums import ActionType
from .pending_actions import PendingActionQueue
from .statuses import TickTiming
from .unit import Unit


@dataclass
class BattleOutcome:
    winner: str
    turns: int
    battle_log: list[str]


class BattleEngine:
    def __init__(self, battle_state: BattleState, ai: SimpleAI | None = None) -> None:
        self.state = battle_state
        self.ai = ai or SimpleAI()
        self.pending: PendingActionQueue = self.state.pending_actions

    def run(self, max_turns: int = 100) -> BattleOutcome:
        self.state.events.emit(EventType.BATTLE_START)
        self.state.events.emit(EventType.WAVE_START, payload={"wave": 1})
        while not self.state.is_finished() and self.state.turn_counter < max_turns:
            if len(self.pending) > 0:
                self._execute_pending()
                continue

            actor = self.state.timeline.next_actor()
            if actor is None:
                break

            if actor.is_defeated():
                self.state.timeline.reschedule(actor)
                continue

            self.state.turn_counter += 1
            self._start_turn(actor)
            if self.state.is_finished():
                break

            if not actor.can_act():
                self.state.add_log(f"[Control] {actor.name} cannot act")
                self._end_turn(actor)
                self.state.timeline.reschedule(actor)
                continue

            if actor.energy_full():
                ult_action = self.ai.choose_action(actor, self.state).action
                if isinstance(ult_action, UltimateAction):
                    self._execute_action(ult_action)
                    if self.state.is_finished():
                        break

            if self.state.is_finished():
                break

            decision = self.ai.choose_action(actor, self.state)
            self._execute_action(decision.action)
            if self.state.is_finished():
                break
            self._end_turn(actor)
            self.state.timeline.reschedule(actor)

        if not self.state.alive_allies() and not self.state.alive_enemies():
            winner = "draw"
        elif self.state.alive_enemies() == []:
            winner = "allies"
        elif self.state.alive_allies() == []:
            winner = "enemies"
        else:
            winner = "draw"
        return BattleOutcome(
            winner=winner,
            turns=self.state.turn_counter,
            battle_log=self.state.battle_log,
        )

    def _execute_pending(self) -> None:
        action = self.pending.pop()
        if action:
            self._execute_action(action)

    def _start_turn(self, unit: Unit) -> None:
        if unit.toughness is not None and unit.toughness.broken:
            unit.toughness.restore()
            self.state.add_log(f"[Recover] {unit.name} restored toughness")
        self.state.events.emit(EventType.TURN_START, actor_id=unit.unit_id)
        for expired in unit.tick_statuses(TickTiming.OWNER_TURN_START):
            self.state.add_log(f"[Status Expire] {unit.name} lost {expired}")
            self.state.events.emit(
                EventType.STATUS_EXPIRE,
                actor_id=unit.unit_id,
                target_id=unit.unit_id,
                payload={"status": expired},
            )

    def _end_turn(self, unit: Unit) -> None:
        for expired in unit.tick_statuses(TickTiming.OWNER_TURN_END):
            self.state.add_log(f"[Status Expire] {unit.name} lost {expired}")
            self.state.events.emit(
                EventType.STATUS_EXPIRE,
                actor_id=unit.unit_id,
                target_id=unit.unit_id,
                payload={"status": expired},
            )
        self.state.events.emit(EventType.TURN_END, actor_id=unit.unit_id)

    def _execute_action(self, action: BaseAction) -> None:
        self.state.events.emit(
            EventType.ACTION_START,
            actor_id=action.actor.unit_id,
            payload={"action": action.config.name},
        )
        try:
            result = action.execute(self.state)
        except ValueError as exc:
            self.state.add_log(f"[Invalid] {exc}")
            return

        self.state.adjust_skill_points(result.sp_delta)
        for target_name, damage in result.damage_done.items():
            self.state.add_log(
                f"[{action.config.action_type.value}] {result.actor} -> {target_name} for {damage}"
            )
        for target_name, absorbed in result.shield_absorbed.items():
            self.state.add_log(f"[Shield Absorb] {target_name} absorbed {absorbed}")
        for target_name, damage in result.toughness_damage_done.items():
            self.state.add_log(f"[Toughness] {target_name} -{damage}")
        for target_name in result.broken_targets:
            self.state.add_log(f"[Break] {target_name} weakness broken")
        for target_name, healed in result.healing_done.items():
            self.state.add_log(f"[Heal] {target_name} +{healed}")
        for target_name, shield in result.shields_added.items():
            self.state.add_log(f"[Shield] {target_name} +{shield}")
        for target_name, names in result.statuses_applied.items():
            for name in names:
                self.state.add_log(f"[Status] {target_name} gained {name}")
        for defeated in result.defeated:
            self.state.add_log(f"[KO] {defeated} defeated")

        if action.config.action_type != ActionType.ULTIMATE:
            self.state.add_log(f"[SP] {self.state.skill_points}/{self.state.max_skill_points}")
        self.state.events.emit(
            EventType.ACTION_END,
            actor_id=action.actor.unit_id,
            payload={"action": action.config.name},
        )
