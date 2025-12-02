from dataclasses import dataclass

from .actions import BaseAction, BasicAttackAction, SkillAction, UltimateAction
from .battle_state import BattleState
from .enums import ActionType, Faction
from .unit import Unit


@dataclass
class Decision:
    action: BaseAction


class SimpleAI:
    def choose_action(self, actor: Unit, battle: BattleState) -> Decision:
        target = self._select_target(actor, battle)
        if not target:
            raise ValueError("No valid targets")

        if actor.energy_full():
            return Decision(self._make_action(actor, target, ActionType.ULTIMATE))

        if battle.skill_points > 0:
            return Decision(self._make_action(actor, target, ActionType.SKILL))

        return Decision(self._make_action(actor, target, ActionType.BASIC))

    def _select_target(self, actor: Unit, battle: BattleState) -> Unit | None:
        candidates = (
            battle.alive_enemies() if actor.faction == Faction.ALLY else battle.alive_allies()
        )
        if not candidates:
            return None
        return min(candidates, key=lambda unit: unit.hp)

    def _make_action(self, actor: Unit, target: Unit, action_type: ActionType) -> BaseAction:
        if action_type == ActionType.BASIC:
            config = actor.kit.basic
            return BasicAttackAction(actor, [target], config)
        if action_type == ActionType.SKILL:
            config = actor.kit.skill
            return SkillAction(actor, [target], config)
        if action_type == ActionType.ULTIMATE:
            config = actor.kit.ultimate
            return UltimateAction(actor, [target], config)
        raise ValueError(f"Unsupported action type: {action_type}")
