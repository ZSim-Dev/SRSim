"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("tag", sa.String(64), nullable=False),
        sa.Column("rarity", sa.Integer(), nullable=False),
        sa.Column("path", sa.String(64), nullable=False),
        sa.Column("element", sa.String(64), nullable=False),
        sa.Column("max_sp", sa.Integer(), nullable=True),
        sa.Column("ranks", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("skills", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("skill_trees", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("icon", sa.String(256), nullable=False),
        sa.Column("preview", sa.String(256), nullable=False),
        sa.Column("portrait", sa.String(256), nullable=False),
        sa.PrimaryKeyConstraint("id", "language"),
    )
    op.create_index("ix_characters_language", "characters", ["language"])

    op.create_table(
        "skills",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("max_level", sa.Integer(), nullable=False),
        sa.Column("element", sa.String(64), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("type_text", sa.String(64), nullable=False),
        sa.Column("effect", sa.String(64), nullable=False),
        sa.Column("effect_text", sa.String(64), nullable=False),
        sa.Column("simple_desc", sa.Text(), nullable=False),
        sa.Column("desc", sa.Text(), nullable=False),
        sa.Column("params", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("icon", sa.String(256), nullable=True),
        sa.PrimaryKeyConstraint("id", "language"),
    )
    op.create_index("ix_skills_language", "skills", ["language"])

    op.create_table(
        "ranks",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("desc", sa.Text(), nullable=False),
        sa.Column("materials", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("icon", sa.String(256), nullable=False),
        sa.Column("level_up_skills", sa.Text(), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("id", "language"),
    )
    op.create_index("ix_ranks_language", "ranks", ["language"])

    op.create_table(
        "skill_trees",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("max_level", sa.Integer(), nullable=False),
        sa.Column("desc", sa.Text(), nullable=False),
        sa.Column("params", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("anchor", sa.String(64), nullable=False),
        sa.Column("pre_points", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("level_up_skills", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("levels", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("icon", sa.String(256), nullable=False),
        sa.PrimaryKeyConstraint("id", "language"),
    )
    op.create_index("ix_skill_trees_language", "skill_trees", ["language"])

    op.create_table(
        "promotions",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("language", sa.String(8), nullable=False),
        sa.Column("values", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("materials", sa.Text(), nullable=False, server_default="[]"),
        sa.PrimaryKeyConstraint("id", "language"),
    )
    op.create_index("ix_promotions_language", "promotions", ["language"])


def downgrade() -> None:
    op.drop_index("ix_promotions_language", table_name="promotions")
    op.drop_table("promotions")

    op.drop_index("ix_skill_trees_language", table_name="skill_trees")
    op.drop_table("skill_trees")

    op.drop_index("ix_ranks_language", table_name="ranks")
    op.drop_table("ranks")

    op.drop_index("ix_skills_language", table_name="skills")
    op.drop_table("skills")

    op.drop_index("ix_characters_language", table_name="characters")
    op.drop_table("characters")
