from dataclasses import dataclass

from .actions import BaseAction, UltimateAction
from .ai import SimpleAI
from .battle_state import BattleState
from .enums import ActionType
from .pending_actions import PendingActionQueue


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

            if actor.energy_full():
                ult_action = self.ai.choose_action(actor, self.state).action
                if isinstance(ult_action, UltimateAction):
                    self._execute_action(ult_action)

            decision = self.ai.choose_action(actor, self.state)
            self._execute_action(decision.action)
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

    def _execute_action(self, action: BaseAction) -> None:
        try:
            result = action.execute(self.state.skill_points)
        except ValueError as exc:
            self.state.add_log(f"[Invalid] {exc}")
            return

        self.state.adjust_skill_points(result.sp_delta)
        for target_name, damage in result.damage_done.items():
            self.state.add_log(
                f"[{action.config.action_type.value}] {result.actor} -> {target_name} for {damage}"
            )
        for defeated in result.defeated:
            self.state.add_log(f"[KO] {defeated} defeated")

        if action.config.action_type != ActionType.ULTIMATE:
            self.state.add_log(f"[SP] {self.state.skill_points}/{self.state.max_skill_points}")
