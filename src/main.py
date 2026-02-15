from srsim.core.abilities import ActionConfig, UnitKit
from srsim.core.battle_state import BattleState
from srsim.core.engine import BattleEngine
from srsim.core.enums import ActionType, Faction
from srsim.core.stats import Stats
from srsim.core.unit import Unit
from srsim.role_api.core.exceptions import AppException
from srsim.role_api.models.role_api import RoleDetailData, RoleListData, RolePanelData
from srsim.role_api.services.role_service import RoleService

_role_service = RoleService()


def _load_role_init_profile(
    *,
    role_name: str,
    language: str,
    level: int,
) -> tuple[str, int, int, int, int]:
    role_list = RoleListData.model_validate(
        _role_service.search_roles(
            language=language,
            path=None,
            element=None,
            name=role_name,
        ).model_dump()
    )
    if not role_list.items:
        raise AppException(message=f"role not found by name: {role_name}")
    role_id = role_list.items[0].id

    detail = RoleDetailData.model_validate(
        _role_service.get_role_detail(language=language, role_id=role_id).model_dump()
    )
    panel = RolePanelData.model_validate(
        _role_service.get_role_panel(
            language=language,
            role_id=role_id,
            level=level,
            promoted=False,
        ).model_dump()
    )

    hp = int(float(panel.stats.get("hp", 0)))
    atk = int(float(panel.stats.get("atk", 0)))
    defense = int(float(panel.stats.get("def", hp * 0.1)))
    spd_raw = panel.stats.get("spd", panel.stats.get("speed", 100))
    spd = int(float(spd_raw))
    if hp <= 0 or atk <= 0 or spd <= 0:
        raise AppException(message=f"invalid role panel stats for role: {role_id}")
    return detail.basic.name, atk, hp, defense if defense > 0 else int(hp * 0.1), spd


def build_unit(unit_id: str, name: str, faction: Faction) -> Unit:
    resolved_name, resolved_atk, resolved_hp, resolved_defense, resolved_spd = (
        _load_role_init_profile(role_name=name, language="en", level=1)
    )

    stats = Stats(
        max_hp=resolved_hp,
        atk=resolved_atk,
        defense=resolved_defense,
        spd=resolved_spd,
        max_energy=100,
    )
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
    return Unit(
        unit_id=unit_id,
        name=resolved_name,
        faction=faction,
        level=1,
        base_stats=stats,
        kit=kit,
    )


def demo_battle() -> None:
    allies = [
        build_unit("ally-1", "Trailblazer", Faction.ALLY),
        build_unit("ally-2", "March 7th", Faction.ALLY),
    ]
    enemies = [
        build_unit("enemy-1", "Automaton", Faction.ENEMY),
    ]
    state = BattleState(allies=allies, enemies=enemies, skill_points=3, max_skill_points=5)
    engine = BattleEngine(state)
    outcome = engine.run(max_turns=50)
    print(f"Battle finished in {outcome.turns} turns. Winner: {outcome.winner}")
    for entry in outcome.battle_log:
        print(entry)


if __name__ == "__main__":
    demo_battle()
