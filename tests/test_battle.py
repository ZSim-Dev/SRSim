from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.stats import Stats
from srsim.core.unit import Unit


def build_test_unit(name: str, faction: Faction) -> Unit:
    stats = Stats(max_hp=800, atk=100, defense=80, spd=100, max_energy=100)
    kit = UnitKit(
        basic=ActionConfig(
            name=f"{name} Basic",
            multiplier=1.0,
            sp_gain=1,
            energy_gain=20,
            action_type=ActionType.BASIC,
        ),
        skill=ActionConfig(
            name=f"{name} Skill",
            multiplier=1.5,
            sp_cost=1,
            energy_gain=25,
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name=f"{name} Ult",
            multiplier=3.0,
            energy_cost=100,
            action_type=ActionType.ULTIMATE,
        ),
    )
    return Unit(unit_id=name, name=name, faction=faction, level=1, base_stats=stats, kit=kit)


def test_battle_runs_to_completion() -> None:
    allies = [build_test_unit("A", Faction.ALLY)]
    enemies = [build_test_unit("B", Faction.ENEMY)]
    state = BattleState(allies=allies, enemies=enemies, skill_points=2, max_skill_points=5)
    outcome = BattleEngine(state).run(max_turns=30)
    assert outcome.winner in {"allies", "enemies", "draw"}
    assert outcome.turns > 0
