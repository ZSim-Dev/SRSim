import pytest

from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.actions import BasicAttackAction
from srsim.core.battle_state import BattleState
from srsim.core.damage import DamageContext, calculate_damage
from srsim.core.elements import Element
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.events import EventType
from srsim.core.pending_actions import InsertedAction, InsertedActionKind, PendingActionQueue
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


def test_speed_change_recalculates_remaining_action_value() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    actor.current_action_value = 70

    actor.recalculate_action_value_for_speed(125)

    assert actor.current_speed == 125
    assert actor.current_action_value == 56
    assert actor.base_action_value == 80


def test_advance_and_delay_apply_immediately_to_remaining_action_value() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    actor.current_action_value = 50

    actor.advance_action(0.3)
    assert actor.current_action_value == 20

    actor.delay_action(0.25)
    assert actor.current_action_value == 45


def test_extra_turn_preserves_action_value_and_does_not_tick_statuses() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    target = build_test_unit("Target", Faction.ENEMY)
    state = BattleState(allies=[actor], enemies=[target], skill_points=0, max_skill_points=5)
    engine = BattleEngine(state)

    actor.energy = actor.base_stats.max_energy
    actor.current_action_value = 37
    marker = StatusTemplate(
        name="Extra Turn Marker",
        kind=StatusKind.BUFF,
        duration=2,
        tick_timing=TickTiming.OWNER_TURN_END,
        effect=StatusEffect(atk_pct=0.1),
    )
    actor.apply_status(marker, actor.unit_id)
    state.grant_extra_turn(actor)

    engine._process_pending()

    assert actor.current_action_value == 37
    assert actor.statuses[0].remaining_turns == 2
    action_starts = [
        event for event in state.events.history if event.event_type == EventType.ACTION_START
    ]
    assert action_starts
    assert action_starts[0].payload["action"] == actor.kit.basic.name
    assert not any(
        event.event_type == EventType.ULTIMATE_INSERTED for event in state.events.history
    )


def test_ultimate_is_inserted_after_action_and_before_next_normal_actor() -> None:
    actor = build_test_unit("Actor", Faction.ALLY)
    actor.base_stats = Stats(max_hp=800, atk=100, defense=80, spd=120, max_energy=100)
    actor.__post_init__()
    actor.energy = actor.base_stats.max_energy

    target = build_test_unit("Target", Faction.ENEMY)
    target.base_stats = Stats(max_hp=5_000, atk=100, defense=80, spd=90, max_energy=100)
    target.__post_init__()

    state = BattleState(allies=[actor], enemies=[target], skill_points=0, max_skill_points=5)
    BattleEngine(state).run(max_turns=2)

    history = state.events.history
    basic_end_index = next(
        index
        for index, event in enumerate(history)
        if event.event_type == EventType.ACTION_END
        and event.payload.get("action") == actor.kit.basic.name
    )
    ultimate_inserted_index = next(
        index
        for index, event in enumerate(history)
        if event.event_type == EventType.ULTIMATE_INSERTED
    )
    ultimate_start_index = next(
        index
        for index, event in enumerate(history)
        if event.event_type == EventType.ACTION_START
        and event.payload.get("action") == actor.kit.ultimate.name
    )
    target_turn_start_index = next(
        index
        for index, event in enumerate(history)
        if event.event_type == EventType.TURN_START and event.actor_id == target.unit_id
    )

    assert (
        basic_end_index < ultimate_inserted_index < ultimate_start_index < target_turn_start_index
    )


def test_inserted_action_queue_uses_priority_then_fifo() -> None:
    first = build_test_unit("First", Faction.ALLY)
    second = build_test_unit("Second", Faction.ALLY)
    third = build_test_unit("Third", Faction.ALLY)
    fourth = build_test_unit("Fourth", Faction.ALLY)
    queue = PendingActionQueue()

    queue.push(InsertedAction(kind=InsertedActionKind.FOLLOW_UP, actor=first))
    queue.push(InsertedAction(kind=InsertedActionKind.EXTRA_TURN, actor=second))
    queue.push(InsertedAction(kind=InsertedActionKind.ULTIMATE, actor=third))
    queue.push(InsertedAction(kind=InsertedActionKind.EXTRA_TURN, actor=fourth))

    pop_order = [queue.pop(), queue.pop(), queue.pop(), queue.pop()]

    assert [item.kind for item in pop_order if item is not None] == [
        InsertedActionKind.ULTIMATE,
        InsertedActionKind.EXTRA_TURN,
        InsertedActionKind.EXTRA_TURN,
        InsertedActionKind.FOLLOW_UP,
    ]
    assert [item.actor.unit_id for item in pop_order if item is not None][1:3] == [
        second.unit_id,
        fourth.unit_id,
    ]
