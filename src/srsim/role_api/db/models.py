import json
from typing import Any

from sqlalchemy import Index, String, Text, event, text
from sqlalchemy.orm import Mapped, mapped_column

from srsim.role_api.db.base import Base


class CharacterModel(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tag: Mapped[str] = mapped_column(String(64), nullable=False)
    rarity: Mapped[int] = mapped_column(nullable=False)
    path: Mapped[str] = mapped_column(String(64), nullable=False)
    element: Mapped[str] = mapped_column(String(64), nullable=False)
    max_sp: Mapped[int | None] = mapped_column(nullable=True)
    ranks: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    skill_trees: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    icon: Mapped[str] = mapped_column(String(256), nullable=False)
    preview: Mapped[str] = mapped_column(String(256), nullable=False)
    portrait: Mapped[str] = mapped_column(String(256), nullable=False)

    __table_args__ = (Index("ix_characters_language", "language"),)

    def get_ranks(self) -> list[str]:
        return json.loads(self.ranks)

    def set_ranks(self, value: list[str]) -> None:
        self.ranks = json.dumps(value)

    def get_skills(self) -> list[str]:
        return json.loads(self.skills)

    def set_skills(self, value: list[str]) -> None:
        self.skills = json.dumps(value)

    def get_skill_trees(self) -> list[str]:
        return json.loads(self.skill_trees)

    def set_skill_trees(self, value: list[str]) -> None:
        self.skill_trees = json.dumps(value)


class SkillModel(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    max_level: Mapped[int] = mapped_column(nullable=False)
    element: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    type_text: Mapped[str] = mapped_column(String(64), nullable=False)
    effect: Mapped[str] = mapped_column(String(64), nullable=False)
    effect_text: Mapped[str] = mapped_column(String(64), nullable=False)
    simple_desc: Mapped[str] = mapped_column(Text, nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    icon: Mapped[str | None] = mapped_column(String(256), nullable=True)

    __table_args__ = (Index("ix_skills_language", "language"),)

    def get_params(self) -> list[list[int | float]]:
        return json.loads(self.params)

    def set_params(self, value: list[list[int | float]]) -> None:
        self.params = json.dumps(value)


class RankModel(Base):
    __tablename__ = "ranks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    rank: Mapped[int] = mapped_column(nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable=False)
    materials: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    icon: Mapped[str] = mapped_column(String(256), nullable=False)
    level_up_skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    __table_args__ = (Index("ix_ranks_language", "language"),)

    def get_materials(self) -> list[dict[str, Any]]:
        return json.loads(self.materials)

    def set_materials(self, value: list[dict[str, Any]]) -> None:
        self.materials = json.dumps(value)

    def get_level_up_skills(self) -> list[dict[str, Any]]:
        return json.loads(self.level_up_skills)

    def set_level_up_skills(self, value: list[dict[str, Any]]) -> None:
        self.level_up_skills = json.dumps(value)


class SkillTreeModel(Base):
    __tablename__ = "skill_trees"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    max_level: Mapped[int] = mapped_column(nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable=False)
    params: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    anchor: Mapped[str] = mapped_column(String(64), nullable=False)
    pre_points: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    level_up_skills: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    levels: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    icon: Mapped[str] = mapped_column(String(256), nullable=False)

    __table_args__ = (Index("ix_skill_trees_language", "language"),)

    def get_params(self) -> list[list[int | float]]:
        return json.loads(self.params)

    def set_params(self, value: list[list[int | float]]) -> None:
        self.params = json.dumps(value)

    def get_pre_points(self) -> list[str]:
        return json.loads(self.pre_points)

    def set_pre_points(self, value: list[str]) -> None:
        self.pre_points = json.dumps(value)

    def get_level_up_skills(self) -> list[dict[str, Any]]:
        return json.loads(self.level_up_skills)

    def set_level_up_skills(self, value: list[dict[str, Any]]) -> None:
        self.level_up_skills = json.dumps(value)

    def get_levels(self) -> list[dict[str, Any]]:
        return json.loads(self.levels)

    def set_levels(self, value: list[dict[str, Any]]) -> None:
        self.levels = json.dumps(value)


class PromotionModel(Base):
    __tablename__ = "promotions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(8), primary_key=True)
    values: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    materials: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    __table_args__ = (Index("ix_promotions_language", "language"),)

    def get_values(self) -> list[dict[str, dict[str, Any]]]:
        return json.loads(self.values)

    def set_values(self, value: list[dict[str, dict[str, Any]]]) -> None:
        self.values = json.dumps(value)

    def get_materials(self) -> list[list[dict[str, Any]]]:
        return json.loads(self.materials)

    def set_materials(self, value: list[list[dict[str, Any]]]) -> None:
        self.materials = json.dumps(value)


# Enable SQLite foreign key support
@event.listens_for(Base.metadata, "after_create")
def _enable_foreign_keys(target, connection, **kw):
    pass  # No-op for SQLite compatibility
