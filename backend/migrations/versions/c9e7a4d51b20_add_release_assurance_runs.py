"""add release assurance runs

Revision ID: c9e7a4d51b20
Revises: 48f2772be5c4
Create Date: 2026-07-24 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9e7a4d51b20"
down_revision: Union[str, Sequence[str], None] = "48f2772be5c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "release_assurance_runs",
        sa.Column("id", sa.String(length=48), nullable=False),
        sa.Column("bundle_id", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("baseline_version", sa.String(length=80), nullable=False),
        sa.Column("candidate_version", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("gate_decision", sa.String(length=40), nullable=False),
        sa.Column("readiness_score", sa.Integer(), nullable=False),
        sa.Column("initiated_by", sa.String(length=120), nullable=False),
        sa.Column("checks_json", sa.JSON(), nullable=False),
        sa.Column("diff_json", sa.JSON(), nullable=False),
        sa.Column("blast_radius_json", sa.JSON(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("decision_json", sa.JSON(), nullable=False),
        sa.Column("attestation_digest", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "attestation_digest",
        "bundle_id",
        "candidate_version",
        "created_at",
        "gate_decision",
        "initiated_by",
        "status",
        "updated_at",
    ):
        op.create_index(
            op.f(f"ix_release_assurance_runs_{column}"),
            "release_assurance_runs",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in (
        "updated_at",
        "status",
        "initiated_by",
        "gate_decision",
        "created_at",
        "candidate_version",
        "bundle_id",
        "attestation_digest",
    ):
        op.drop_index(op.f(f"ix_release_assurance_runs_{column}"), table_name="release_assurance_runs")
    op.drop_table("release_assurance_runs")
