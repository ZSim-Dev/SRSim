from math import isclose

from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.damage import DamageContext, calculate_damage
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.stats import Stats
from srsim.core.timeline import Timeline
from srsim.core.unit import CombatModifiers, ToughnessState, Unit


def build_test_unit(name: str, faction: Faction, spd: int = 100) -> Unit:
    stats = Stats(max_hp=800, atk=100, defense=80, spd=spd, max_energy=100)
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
    return Unit(unit_id=name, name=name, faction=faction, level=80, base_stats=stats, kit=kit)


def test_battle_runs_to_completion() -> None:
    allies = [build_test_unit("A", Faction.ALLY)]
    enemies = [build_test_unit("B", Faction.ENEMY)]
    state = BattleState(allies=allies, enemies=enemies, skill_points=2, max_skill_points=5)
    outcome = BattleEngine(state).run(max_turns=30)
    assert outcome.winner in {"allies", "enemies", "draw"}
    assert outcome.turns > 0


def test_speed_change_recalculates_remaining_action_value() -> None:
    unit = build_test_unit("A", Faction.ALLY, spd=100)
    unit.speed_tick(40.0)

    unit.set_speed(125.0)

    assert isclose(unit.current_action_value, 48.0, rel_tol=0.0, abs_tol=1e-6)
    assert isclose(unit.speed_state.current_ag, 6000.0, rel_tol=0.0, abs_tol=1e-6)


def test_advance_forward_uses_action_gauge_math() -> None:
    unit = build_test_unit("A", Faction.ALLY, spd=100)

    unit.modify_action_gauge(advance_ratio=0.5)

    assert isclose(unit.current_action_value, 50.0, rel_tol=0.0, abs_tol=1e-6)
    assert isclose(unit.speed_state.current_ag, 5000.0, rel_tol=0.0, abs_tol=1e-6)


def test_timeline_uses_action_value_then_spawn_order() -> None:
    slow = build_test_unit("Slow", Faction.ALLY, spd=100)
    fast = build_test_unit("Fast", Faction.ENEMY, spd=125)
    timeline = Timeline([slow, fast])

    first_actor = timeline.next_actor()
    assert first_actor is fast

    timeline.reschedule(first_actor)
    second_actor = timeline.next_actor()

    assert second_actor is slow


def test_damage_formula_applies_def_resistance_vulnerability_and_broken() -> None:
    attacker = build_test_unit("A", Faction.ALLY)
    defender = build_test_unit("B", Faction.ENEMY)
    attacker.base_stats = Stats(
        max_hp=800,
        atk=1000,
        defense=100,
        spd=100,
        crit_rate=1.0,
        crit_dmg=1.0,
        dmg_boost=0.5,
        max_energy=100,
    )
    attacker.hp = attacker.base_stats.max_hp
    attacker.modifiers = CombatModifiers(defense_ignore=0.2, res_pen=0.1)
    defender.base_stats = Stats(
        max_hp=1200,
        atk=100,
        defense=400,
        spd=90,
        max_energy=100,
        resistance=0.2,
    )
    defender.hp = defender.base_stats.max_hp
    defender.modifiers = CombatModifiers(vulnerability=0.25, mitigation=0.1)
    defender.toughness = ToughnessState(current=0, maximum=90, broken=True)

    damage = calculate_damage(DamageContext(attacker=attacker, defender=defender, multiplier=2.0))

    assert damage == 3375
