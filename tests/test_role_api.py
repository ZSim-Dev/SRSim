import asyncio
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from srsim.role_api.api import role as role_api
from srsim.role_api.core.exception_handlers import register_exception_handlers
from srsim.role_api.db.session import DatabaseSessionManager, set_session_manager
from srsim.role_api.services.db_rebuild_service import DbRebuildService
from srsim.role_api.services.role_data_loader import RoleDataLoader
from srsim.role_api.services.role_service import RoleService


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _prepare_role_data(root: Path) -> Path:
    data_root = root / "index_new" / "en"
    data_root.mkdir(parents=True)

    _write_json(
        data_root / "characters.json",
        {
            "1001": {
                "id": "1001",
                "name": "Trailblazer",
                "tag": "sample",
                "rarity": 5,
                "path": "Warrior",
                "element": "Physical",
                "max_sp": 120,
                "ranks": ["rank_2", "rank_1"],
                "skills": ["skill_2", "skill_1"],
                "skill_trees": ["tree_2", "tree_1"],
                "icon": "icon.png",
                "preview": "preview.png",
                "portrait": "portrait.png",
            }
        },
    )
    _write_json(
        data_root / "character_skills.json",
        {
            "skill_1": {
                "id": "skill_1",
                "name": "Sample Skill",
                "max_level": 1,
                "element": "Physical",
                "type": "Normal",
                "type_text": "Normal",
                "effect": "Damage",
                "effect_text": "Damage",
                "simple_desc": "Deals #1[i] damage.",
                "desc": "Deals #1[i] damage.",
                "params": [[100]],
                "icon": "skill.png",
            },
            "skill_2": {
                "id": "skill_2",
                "name": "Follow-up Skill",
                "max_level": 1,
                "element": "Physical",
                "type": "Ultra",
                "type_text": "Ultra",
                "effect": "Buff",
                "effect_text": "Buff",
                "simple_desc": "Boosts #1[i] attack.",
                "desc": "Boosts #1[i] attack.",
                "params": [[25]],
                "icon": "skill2.png",
            },
        },
    )
    _write_json(
        data_root / "character_ranks.json",
        {
            "rank_1": {
                "id": "rank_1",
                "name": "Rank 1",
                "rank": 1,
                "desc": "rank",
                "materials": [{"id": "item_1", "num": 1}],
                "icon": "rank.png",
                "level_up_skills": [{"id": "skill_1", "num": 1}],
            },
            "rank_2": {
                "id": "rank_2",
                "name": "Rank 2",
                "rank": 2,
                "desc": "rank2",
                "materials": [{"id": "item_2", "num": 2}],
                "icon": "rank2.png",
                "level_up_skills": [{"id": "skill_2", "num": 1}],
            },
        },
    )
    _write_json(
        data_root / "character_skill_trees.json",
        {
            "tree_1": {
                "id": "tree_1",
                "name": "Trace",
                "max_level": 1,
                "desc": "trace",
                "params": [[1]],
                "anchor": "Point01",
                "pre_points": [],
                "level_up_skills": [{"id": "skill_1", "num": 1}],
                "levels": [
                    {
                        "promotion": 0,
                        "level": 1,
                        "properties": [],
                        "materials": [{"id": "item_1", "num": 1}],
                    }
                ],
                "icon": "tree.png",
            },
            "tree_2": {
                "id": "tree_2",
                "name": "Trace 2",
                "max_level": 1,
                "desc": "trace2",
                "params": [[2]],
                "anchor": "Point02",
                "pre_points": ["tree_1"],
                "level_up_skills": [{"id": "skill_2", "num": 1}],
                "levels": [
                    {
                        "promotion": 0,
                        "level": 1,
                        "properties": [],
                        "materials": [{"id": "item_2", "num": 2}],
                    }
                ],
                "icon": "tree2.png",
            },
        },
    )
    _write_json(
        data_root / "character_promotions.json",
        {
            "1001": {
                "id": "1001",
                "values": [
                    {
                        "hp": {"base": 1000, "step": 10},
                        "atk": {"base": 100, "step": 2},
                        "def": {"base": 80, "step": 1},
                        "spd": {"base": 100, "step": 0},
                    }
                ],
                "materials": [[{"id": "item_1", "num": 1}]],
            }
        },
    )
    return root / "index_new"


async def _setup_database(db_path: Path, data_root: Path) -> DatabaseSessionManager:
    """Set up the database with test data."""
    session_manager = DatabaseSessionManager.from_path(db_path)
    set_session_manager(session_manager)

    # Create tables and load data
    await session_manager.create_tables()
    async with session_manager.session() as session:
        rebuild_service = DbRebuildService(session, data_root=data_root)
        await rebuild_service.rebuild_language("en")

    return session_manager


def test_role_loader_reads_env_data_root(monkeypatch, tmp_path: Path) -> None:
    data_root = _prepare_role_data(tmp_path)
    monkeypatch.setenv("SRSIM_ROLE_DATA_ROOT", str(data_root))

    loader = RoleDataLoader()
    assert loader.supported_languages() == ["en"]


def test_list_roles_and_panel_from_fastapi(tmp_path: Path) -> None:
    data_root = _prepare_role_data(tmp_path)
    db_path = tmp_path / "test.db"

    # Run async setup in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        session_manager = loop.run_until_complete(_setup_database(db_path, data_root))
    finally:
        pass  # Keep the loop alive for the test

    app = FastAPI(title="test-role-api")
    register_exception_handlers(app)
    role_api._service = RoleService(loader=RoleDataLoader(data_root=data_root))
    app.include_router(role_api.router)

    with TestClient(app, raise_server_exceptions=True) as client:
        list_response = client.get("/roles", params={"language": "en", "offset": 0, "limit": 5})
        assert list_response.status_code == 200
        list_payload = list_response.json()
        assert list_payload["code"] == 0
        role_id = list_payload["data"]["items"][0]["id"]

        panel_response = client.get(
            f"/roles/{role_id}/panel",
            params={"language": "en", "level": 1},
        )
        assert panel_response.status_code == 200
        panel_payload = panel_response.json()
        assert panel_payload["code"] == 0
        assert panel_payload["data"]["stats"]["hp"] == 1000

        detail_response = client.get(f"/roles/{role_id}", params={"language": "en"})
        assert detail_response.status_code == 200
        detail_payload = detail_response.json()
        assert detail_payload["code"] == 0
        assert [skill["id"] for skill in detail_payload["data"]["skills"]] == ["skill_2", "skill_1"]
        assert [rank["id"] for rank in detail_payload["data"]["ranks"]] == ["rank_2", "rank_1"]
        assert [tree["id"] for tree in detail_payload["data"]["skillTrees"]] == [
            "tree_2",
            "tree_1",
        ]

    # Cleanup
    loop.run_until_complete(session_manager.close())
    loop.close()
