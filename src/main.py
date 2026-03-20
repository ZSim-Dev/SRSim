from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.stats import Stats
from srsim.core.unit import Unit


def build_demo_unit(
    *,
    unit_id: str,
    name: str,
    faction: Faction,
    hp: int,
    atk: int,
    defense: int,
    spd: int,
) -> Unit:
    stats = Stats(
        max_hp=hp,
        atk=atk,
        defense=defense,
        spd=spd,
        max_energy=100,
    )
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
            multiplier=1.6,
            sp_cost=1,
            energy_gain=30,
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name=f"{name} Ultimate",
            multiplier=3.0,
            energy_cost=100,
            action_type=ActionType.ULTIMATE,
        ),
    )
    return Unit(
        unit_id=unit_id,
        name=name,
        faction=faction,
        level=1,
        base_stats=stats,
        kit=kit,
    )


def demo_battle() -> None:
    hero = build_demo_unit(
        unit_id="ally-1",
        name="Demo Hero",
        faction=Faction.ALLY,
        hp=900,
        atk=120,
        defense=90,
        spd=105,
    )
    slime = build_demo_unit(
        unit_id="enemy-1",
        name="Demo Slime",
        faction=Faction.ENEMY,
        hp=700,
        atk=85,
        defense=60,
        spd=95,
    )

    state = BattleState(allies=[hero], enemies=[slime], skill_points=3, max_skill_points=5)
    outcome = BattleEngine(state).run(max_turns=30)

    print("=== SRSim Minimal Battle Demo ===")
    print(f"Turns: {outcome.turns}")
    print(f"Winner: {outcome.winner}")
    print(f"Hero HP: {hero.hp}/{hero.base_stats.max_hp} | Energy: {hero.energy}/{hero.base_stats.max_energy}")
    print(
        f"Enemy HP: {slime.hp}/{slime.base_stats.max_hp} | "
        f"Energy: {slime.energy}/{slime.base_stats.max_energy}"
    )
    print("\nBattle Log:")
    for entry in outcome.battle_log:
        print(f"- {entry}")


if __name__ == "__main__":
    demo_battle()
