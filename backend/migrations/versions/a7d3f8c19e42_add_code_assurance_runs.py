"""add code assurance runs

Revision ID: a7d3f8c19e42
Revises: c9e7a4d51b20
Create Date: 2026-07-25 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7d3f8c19e42"
down_revision: Union[str, Sequence[str], None] = "c9e7a4d51b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "code_assurance_runs",
        sa.Column("id", sa.String(length=48), nullable=False),
        sa.Column("tenant_id", sa.String(length=80), nullable=False),
        sa.Column("repository_id", sa.String(length=120), nullable=False),
        sa.Column("commit_sha", sa.String(length=40), nullable=False),
        sa.Column("scanner_profile", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=48), nullable=False),
        sa.Column("policy_decision", sa.String(length=40), nullable=False),
        sa.Column("initiated_by", sa.String(length=120), nullable=False),
        sa.Column("findings_json", sa.JSON(), nullable=False),
        sa.Column("sarif_summary_json", sa.JSON(), nullable=False),
        sa.Column("attack_path_json", sa.JSON(), nullable=False),
        sa.Column("remediation_json", sa.JSON(), nullable=False),
        sa.Column("validation_json", sa.JSON(), nullable=False),
        sa.Column("evidence_digest", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "commit_sha",
        "created_at",
        "evidence_digest",
        "initiated_by",
        "policy_decision",
        "repository_id",
        "scanner_profile",
        "status",
        "tenant_id",
        "updated_at",
    ):
        op.create_index(
            op.f(f"ix_code_assurance_runs_{column}"),
            "code_assurance_runs",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in (
        "updated_at",
        "tenant_id",
        "status",
        "scanner_profile",
        "repository_id",
        "policy_decision",
        "initiated_by",
        "evidence_digest",
        "created_at",
        "commit_sha",
    ):
        op.drop_index(op.f(f"ix_code_assurance_runs_{column}"), table_name="code_assurance_runs")
    op.drop_table("code_assurance_runs")
