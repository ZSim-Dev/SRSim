import pytest

from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.actions import BasicAttackAction
from srsim.core.battle_state import BattleState
from srsim.core.damage import DamageContext, calculate_damage
from srsim.core.elements import Element
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.events import EventType
from srsim.core.stats import Stats
from srsim.core.statuses import StatusEffect, StatusKind, StatusTemplate, TickTiming
from srsim.core.timeline import Timeline
from srsim.core.toughness import ToughnessState
from srsim.core.unit import Unit

TEST_BUFF = StatusTemplate(
    name="Test Buff",
    kind=StatusKind.BUFF,
    duration=2,
    tick_timing=TickTiming.OWNER_TURN_END,
    effect=StatusEffect(atk_pct=0.2),
)


def build_test_unit(name: str, faction: Faction) -> Unit:
    stats = Stats(max_hp=800, atk=100, defense=80, spd=100, max_energy=100)
    kit = UnitKit(
        basic=ActionConfig(
            name=f"{name} Basic",
            multiplier=1.0,
            element=Element.PHYSICAL,
            toughness_damage=30,
            sp_gain=1,
            energy_gain=20,
            action_type=ActionType.BASIC,
        ),
        skill=ActionConfig(
            name=f"{name} Skill",
            multiplier=1.5,
            element=Element.PHYSICAL,
            sp_cost=1,
            energy_gain=30,
            self_shield_multiplier=0.5,
            actor_statuses=(TEST_BUFF,),
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name=f"{name} Ult",
            multiplier=3.0,
            element=Element.PHYSICAL,
            energy_cost=100,
            energy_gain=5,
            self_heal_multiplier=0.4,
            action_type=ActionType.ULTIMATE,
        ),
    )
    toughness = None
    if faction == Faction.ENEMY:
        toughness = ToughnessState(
            max_toughness=60,
            weaknesses=frozenset({Element.PHYSICAL}),
        )
    return Unit(
        unit_id=name,
        name=name,
        faction=faction,
        level=1,
        base_stats=stats,
        kit=kit,
        element=Element.PHYSICAL,
        toughness=toughness,
    )


def test_battle_runs_to_completion() -> None:
    allies = [build_test_unit("A", Faction.ALLY)]
    enemies = [build_test_unit("B", Faction.ENEMY)]
    state = BattleState(allies=allies, enemies=enemies, skill_points=2, max_skill_points=5)
    outcome = BattleEngine(state).run(max_turns=30)
    assert outcome.winner in {"allies", "enemies", "draw"}
    assert outcome.turns > 0


def test_faster_unit_acts_first_and_more_often() -> None:
    slow = build_test_unit("Slow", Faction.ALLY)
    fast = build_test_unit("Fast", Faction.ENEMY)
    slow.base_stats.spd = 100
    fast.base_stats.spd = 125
    slow.__post_init__()
    fast.__post_init__()

    timeline = Timeline([slow, fast])
    action_order: list[str] = []

    for _ in range(9):
        actor = timeline.next_actor()
        assert actor is not None
        action_order.append(actor.name)
        timeline.reschedule(actor)

    assert action_order[0] == "Fast"
    assert action_order.count("Fast") == 5
    assert action_order.count("Slow") == 4


def test_energy_gain_reports_actual_delta_when_capped() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ENEMY)
    actor.energy = 90

    action = BasicAttackAction(actor, [target], actor.kit.basic)
    result = action.execute(0)

    assert actor.energy == 100
    assert result.energy_delta[actor.name] == 10


def test_skill_applies_shield_and_status() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ENEMY)
    state = BattleState(allies=[actor], enemies=[target], skill_points=3, max_skill_points=5)

    result = actor.kit.skill
    action = BattleEngine(state).ai._make_action(actor, target, result.action_type)
    executed = action.execute(state)

    assert actor.shield > 0
    assert "Test Buff" in [status.name for status in actor.statuses]
    assert executed.shields_added[actor.name] > 0


def test_basic_attack_breaks_weakness_and_emits_event() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ENEMY)
    state = BattleState(allies=[actor], enemies=[target], skill_points=0, max_skill_points=5)

    action = BasicAttackAction(actor, [target], actor.kit.basic)
    action.execute(state)
    action.execute(state)

    assert target.toughness is not None
    assert target.toughness.broken
    assert any(event.event_type == EventType.WEAKNESS_BREAK for event in state.events.history)


def test_damage_uses_expected_crit_when_did_crit_is_unknown() -> None:
    crit_buff = StatusTemplate(
        name="Crit Buff",
        kind=StatusKind.BUFF,
        duration=2,
        tick_timing=TickTiming.OWNER_TURN_END,
        effect=StatusEffect(crit_rate=0.5, crit_dmg=1.0),
    )
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ENEMY)

    base_damage = calculate_damage(
        DamageContext(
            attacker=actor,
            defender=target,
            multiplier=1.0,
            element=Element.PHYSICAL,
        )
    )
    actor.apply_status(crit_buff, actor.unit_id)
    expected_damage = calculate_damage(
        DamageContext(
            attacker=actor,
            defender=target,
            multiplier=1.0,
            element=Element.PHYSICAL,
        )
    )
    forced_crit_damage = calculate_damage(
        DamageContext(
            attacker=actor,
            defender=target,
            multiplier=1.0,
            element=Element.PHYSICAL,
            did_crit=True,
        )
    )

    assert base_damage < expected_damage < forced_crit_damage


def test_multiple_mitigation_effects_stack_multiplicatively() -> None:
    first_mitigation = StatusTemplate(
        name="Mitigation One",
        kind=StatusKind.BUFF,
        duration=2,
        tick_timing=TickTiming.OWNER_TURN_END,
        effect=StatusEffect(mitigation=0.3),
    )
    second_mitigation = StatusTemplate(
        name="Mitigation Two",
        kind=StatusKind.BUFF,
        duration=2,
        tick_timing=TickTiming.OWNER_TURN_END,
        effect=StatusEffect(mitigation=0.3),
    )
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ALLY)

    base_damage = calculate_damage(
        DamageContext(
            attacker=actor,
            defender=target,
            multiplier=1.0,
            element=Element.PHYSICAL,
        )
    )
    target.apply_status(first_mitigation, actor.unit_id)
    target.apply_status(second_mitigation, actor.unit_id)

    actual_damage = calculate_damage(
        DamageContext(
            attacker=actor,
            defender=target,
            multiplier=1.0,
            element=Element.PHYSICAL,
        )
    )

    assert target.damage_mitigation() == pytest.approx(0.51)
    assert actual_damage == 17
    assert actual_damage > int(base_damage * (1.0 - 0.6))


def test_defeated_target_does_not_receive_break_or_statuses() -> None:
    lethal_status = StatusTemplate(
        name="Lethal Mark",
        kind=StatusKind.DEBUFF,
        duration=1,
        tick_timing=TickTiming.OWNER_TURN_END,
        effect=StatusEffect(),
    )
    actor_stats = Stats(max_hp=100, atk=10_000, defense=80, spd=100, max_energy=100)
    target_stats = Stats(max_hp=1, atk=100, defense=0, spd=100, max_energy=100)
    actor = build_test_unit("Actor", Faction.ALLY)
    actor.base_stats = actor_stats
    actor.__post_init__()
    target = build_test_unit("Target", Faction.ENEMY)
    target.base_stats = target_stats
    target.__post_init__()

    action_config = ActionConfig(
        name="Lethal Attack",
        multiplier=1.0,
        element=Element.PHYSICAL,
        toughness_damage=60,
        target_statuses=(lethal_status,),
        action_type=ActionType.BASIC,
    )
    action = BasicAttackAction(actor, [target], action_config)
    result = action.execute(0)

    assert target.is_defeated()
    assert target.toughness is not None
    assert not target.toughness.broken
    assert target.statuses == []
    assert result.broken_targets == []
    assert result.statuses_applied == {}


def test_kill_energy_and_events_count_same_name_targets_separately() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    actor.base_stats = Stats(max_hp=100, atk=10_000, defense=80, spd=100, max_energy=100)
    actor.__post_init__()
    target_a = build_test_unit("Shared", Faction.ENEMY)
    target_a.unit_id = "shared-a"
    target_a.base_stats = Stats(max_hp=1, atk=100, defense=0, spd=100, max_energy=100)
    target_a.__post_init__()
    target_b = build_test_unit("Shared", Faction.ENEMY)
    target_b.unit_id = "shared-b"
    target_b.base_stats = Stats(max_hp=1, atk=100, defense=0, spd=100, max_energy=100)
    target_b.__post_init__()
    state = BattleState(
        allies=[actor],
        enemies=[target_a, target_b],
        skill_points=0,
        max_skill_points=5,
    )

    action = BasicAttackAction(actor, [target_a, target_b], actor.kit.basic)
    result = action.execute(state)
    kill_events = [event for event in state.events.history if event.event_type == EventType.KILL]

    assert target_a.is_defeated()
    assert target_b.is_defeated()
    assert actor.energy == 40
    assert result.energy_delta[actor.name] == 40
    assert result.defeated == ["Shared", "Shared"]
    assert len(kill_events) == 2
    assert {event.target_id for event in kill_events} == {"shared-a", "shared-b"}
