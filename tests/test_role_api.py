import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from srsim.role_api.api import role as role_api
from srsim.role_api.core.exception_handlers import register_exception_handlers
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
                "ranks": ["rank_1"],
                "skills": ["skill_1"],
                "skill_trees": ["tree_1"],
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
            }
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
            }
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
            }
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


def _build_client(data_root: Path) -> TestClient:
    app = FastAPI(title="test-role-api")
    register_exception_handlers(app)
    role_api._service = RoleService(loader=RoleDataLoader(data_root=data_root))
    app.include_router(role_api.router)
    return TestClient(app)


def test_role_loader_reads_env_data_root(monkeypatch, tmp_path: Path) -> None:
    data_root = _prepare_role_data(tmp_path)
    monkeypatch.setenv("SRSIM_ROLE_DATA_ROOT", str(data_root))

    loader = RoleDataLoader()
    assert loader.supported_languages() == ["en"]


def test_list_roles_and_panel_from_fastapi(tmp_path: Path) -> None:
    data_root = _prepare_role_data(tmp_path)
    client = _build_client(data_root)

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
