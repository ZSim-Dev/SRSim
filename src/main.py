from __future__ import annotations

from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.stats import Stats
from srsim.core.unit import Unit


def build_unit(unit_id: str, name: str, faction: Faction, atk: int, hp: int, spd: int) -> Unit:
    stats = Stats(max_hp=hp, atk=atk, defense=int(hp * 0.1), spd=spd, max_energy=100)
    kit = UnitKit(
        basic=ActionConfig(
            name="Basic Attack",
            multiplier=1.0,
            sp_gain=1,
            energy_gain=20,
            action_type=ActionType.BASIC,
        ),
        skill=ActionConfig(
            name="Skill",
            multiplier=1.6,
            sp_cost=1,
            energy_gain=30,
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name="Ultimate",
            multiplier=3.0,
            energy_cost=100,
            action_type=ActionType.ULTIMATE,
        ),
    )
    return Unit(unit_id=unit_id, name=name, faction=faction, level=1, base_stats=stats, kit=kit)


def demo_battle() -> None:
    allies = [
        build_unit("ally-1", "Trailblazer", Faction.ALLY, atk=120, hp=1200, spd=104),
        build_unit("ally-2", "March 7th", Faction.ALLY, atk=95, hp=1000, spd=106),
    ]
    enemies = [
        build_unit("enemy-1", "Automaton", Faction.ENEMY, atk=110, hp=1800, spd=98),
    ]
    state = BattleState(allies=allies, enemies=enemies, skill_points=3, max_skill_points=5)
    engine = BattleEngine(state)
    outcome = engine.run(max_turns=50)
    print(f"Battle finished in {outcome.turns} turns. Winner: {outcome.winner}")
    for entry in outcome.battle_log:
        print(entry)


if __name__ == "__main__":
    demo_battle()
