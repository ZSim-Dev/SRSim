from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.engine import BattleEngine
from srsim.core.elements import Element
from srsim.core.enums import ActionType, Faction
from srsim.core.events import EventType
from srsim.core.stats import Stats
from srsim.core.statuses import StatusEffect, StatusKind, StatusTemplate, TickTiming
from srsim.core.toughness import ToughnessState
from srsim.core.unit import Unit


BRAVERY = StatusTemplate(
    name="Bravery",
    kind=StatusKind.BUFF,
    duration=2,
    tick_timing=TickTiming.OWNER_TURN_END,
    effect=StatusEffect(atk_pct=0.25, dmg_boost=0.15),
)

EXPOSE = StatusTemplate(
    name="Expose",
    kind=StatusKind.DEBUFF,
    duration=2,
    tick_timing=TickTiming.OWNER_TURN_END,
    effect=StatusEffect(vulnerability=0.2),
)

WEAKENED = StatusTemplate(
    name="Weakened",
    kind=StatusKind.DEBUFF,
    duration=1,
    tick_timing=TickTiming.OWNER_TURN_END,
    effect=StatusEffect(weaken=0.2),
)


def build_demo_unit(
    *,
    unit_id: str,
    name: str,
    faction: Faction,
    element: Element,
    hp: int,
    atk: int,
    defense: int,
    spd: int,
    toughness: ToughnessState | None,
    kit: UnitKit,
) -> Unit:
    stats = Stats(
        max_hp=hp,
        atk=atk,
        defense=defense,
        spd=spd,
        max_energy=100,
    )
    return Unit(
        unit_id=unit_id,
        name=name,
        faction=faction,
        level=1,
        base_stats=stats,
        kit=kit,
        element=element,
        toughness=toughness,
    )


def demo_battle() -> None:
    hero_kit = UnitKit(
        basic=ActionConfig(
            name="Demo Hero Basic",
            multiplier=1.0,
            element=Element.PHYSICAL,
            toughness_damage=30,
            sp_gain=1,
            energy_gain=20,
            action_type=ActionType.BASIC,
        ),
        skill=ActionConfig(
            name="Demo Hero Skill",
            multiplier=1.4,
            element=Element.PHYSICAL,
            toughness_damage=30,
            sp_cost=1,
            energy_gain=30,
            self_shield_multiplier=0.5,
            actor_statuses=(BRAVERY,),
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name="Demo Hero Ultimate",
            multiplier=2.4,
            element=Element.PHYSICAL,
            toughness_damage=60,
            energy_cost=100,
            energy_gain=5,
            self_heal_multiplier=0.5,
            self_heal_flat=30,
            target_statuses=(EXPOSE,),
            action_type=ActionType.ULTIMATE,
        ),
    )
    slime_kit = UnitKit(
        basic=ActionConfig(
            name="Demo Slime Basic",
            multiplier=0.9,
            element=Element.FIRE,
            energy_gain=20,
            action_type=ActionType.BASIC,
        ),
        skill=ActionConfig(
            name="Demo Slime Skill",
            multiplier=1.1,
            element=Element.FIRE,
            energy_gain=30,
            target_statuses=(WEAKENED,),
            action_type=ActionType.SKILL,
        ),
        ultimate=ActionConfig(
            name="Demo Slime Ultimate",
            multiplier=1.8,
            element=Element.FIRE,
            energy_cost=100,
            energy_gain=5,
            action_type=ActionType.ULTIMATE,
        ),
    )

    hero = build_demo_unit(
        unit_id="ally-1",
        name="Demo Hero",
        faction=Faction.ALLY,
        element=Element.PHYSICAL,
        hp=900,
        atk=120,
        defense=90,
        spd=105,
        toughness=None,
        kit=hero_kit,
    )
    slime = build_demo_unit(
        unit_id="enemy-1",
        name="Demo Slime",
        faction=Faction.ENEMY,
        element=Element.FIRE,
        hp=700,
        atk=85,
        defense=60,
        spd=95,
        toughness=ToughnessState(
            max_toughness=60,
            weaknesses=frozenset({Element.PHYSICAL}),
        ),
        kit=slime_kit,
    )

    state = BattleState(allies=[hero], enemies=[slime], skill_points=3, max_skill_points=5)
    outcome = BattleEngine(state).run(max_turns=30)

    print("=== SRSim Minimal Battle Demo ===")
    print(f"Turns: {outcome.turns}")
    print(f"Winner: {outcome.winner}")
    print(
        f"Hero HP: {hero.hp}/{hero.base_stats.max_hp} | "
        f"Shield: {hero.shield} | Energy: {hero.energy}/{hero.base_stats.max_energy}"
    )
    print(
        f"Enemy HP: {slime.hp}/{slime.base_stats.max_hp} | Toughness: "
        f"{slime.toughness.current_toughness if slime.toughness else 0}/"
        f"{slime.toughness.max_toughness if slime.toughness else 0} | "
        f"Energy: {slime.energy}/{slime.base_stats.max_energy}"
    )
    event_counts: dict[str, int] = {}
    for event in state.events.history:
        event_counts[event.event_type.value] = event_counts.get(event.event_type.value, 0) + 1

    print("\nEvent Counts:")
    for event_type in (
        EventType.BATTLE_START,
        EventType.TURN_START,
        EventType.ACTION_START,
        EventType.SHIELD_APPLIED,
        EventType.STATUS_APPLY,
        EventType.TOUGHNESS_DAMAGE,
        EventType.WEAKNESS_BREAK,
        EventType.HEAL_DONE,
        EventType.ACTION_END,
    ):
        print(f"- {event_type.value}: {event_counts.get(event_type.value, 0)}")

    print("\nBattle Log:")
    for entry in outcome.battle_log:
        print(f"- {entry}")


if __name__ == "__main__":
    demo_battle()
