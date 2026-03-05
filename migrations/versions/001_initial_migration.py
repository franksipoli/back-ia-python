"""Initial migration - Create users, refresh_tokens, email_verifications, phone_verifications tables.

Revision ID: 001
Revises: 
Create Date: 2026-03-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Cria tipos ENUM (o Alembic/SQLAlchemy cuida de duplicatas)
    from sqlalchemy.dialects.postgresql import ENUM
    
    # Create users table first (sem ser afetados pelos ENUMs)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("cpf_cnpj", sa.String(14), nullable=False),
        sa.Column("celular", sa.String(11), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("cpf_cnpj"),
        sa.UniqueConstraint("celular"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_cpf_cnpj"), "users", ["cpf_cnpj"], unique=True)
    op.create_index(op.f("ix_users_celular"), "users", ["celular"], unique=True)

    # Create refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(500), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_refresh_tokens_user_id"), "refresh_tokens", ["user_id"])
    op.create_index(
        op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=True
    )

    # Create email_verifications table
    op.create_table(
        "email_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("token_hash", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        op.f("ix_email_verifications_user_id"), "email_verifications", ["user_id"]
    )
    op.create_index(
        op.f("ix_email_verifications_token_hash"), "email_verifications", ["token_hash"], unique=True
    )

    # Create phone_verifications table
    op.create_table(
        "phone_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(11), nullable=False),
        sa.Column("token_hash", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        op.f("ix_phone_verifications_user_id"), "phone_verifications", ["user_id"]
    )
    op.create_index(
        op.f("ix_phone_verifications_token_hash"), "phone_verifications", ["token_hash"], unique=True
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("phone_verifications")
    op.drop_table("email_verifications")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    # Drop enums
    role_enum = postgresql.ENUM("ADMIN", "USER", name="roleenum")
    role_enum.drop(op.get_bind(), checkfirst=True)

    verification_status_enum = postgresql.ENUM(
        "PENDING", "VERIFIED", "EXPIRED", name="verificationstatusenum"
    )
    verification_status_enum.drop(op.get_bind(), checkfirst=True)
