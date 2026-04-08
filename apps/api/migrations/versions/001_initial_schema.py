"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # tenants
    # ------------------------------------------------------------------
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("business_type", sa.String(50), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="TRY"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)

    # ------------------------------------------------------------------
    # branches
    # ------------------------------------------------------------------
    op.create_table(
        "branches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # categories
    # ------------------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # products
    # ------------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("category_id", sa.String(36), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_in_stock", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # product_tags
    # ------------------------------------------------------------------
    op.create_table(
        "product_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("tag", sa.String(100), nullable=False),
    )

    # ------------------------------------------------------------------
    # modifier_groups
    # ------------------------------------------------------------------
    op.create_table(
        "modifier_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("selection_type", sa.String(20), nullable=False, server_default="single"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("min_select", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_select", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # ------------------------------------------------------------------
    # modifier_options
    # ------------------------------------------------------------------
    op.create_table(
        "modifier_options",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "modifier_group_id",
            sa.String(36),
            sa.ForeignKey("modifier_groups.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("extra_price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # ------------------------------------------------------------------
    # product_modifier_groups  (join table)
    # ------------------------------------------------------------------
    op.create_table(
        "product_modifier_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column(
            "modifier_group_id",
            sa.String(36),
            sa.ForeignKey("modifier_groups.id"),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # orders
    # ------------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("order_number", sa.Integer(), nullable=False),
        sa.Column("order_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("table_number", sa.String(20), nullable=True),
        sa.Column("customer_note", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="TRY"),
        sa.Column("placed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_orders_tenant_status", "orders", ["tenant_id", "status"])
    op.create_index("ix_orders_tenant_placed_at", "orders", ["tenant_id", "placed_at"])

    # ------------------------------------------------------------------
    # order_items
    # ------------------------------------------------------------------
    op.create_table(
        "order_items",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_id", sa.String(36), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("product_name_snapshot", sa.String(255), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
    )

    # ------------------------------------------------------------------
    # order_item_modifiers
    # ------------------------------------------------------------------
    op.create_table(
        "order_item_modifiers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("order_item_id", sa.String(36), sa.ForeignKey("order_items.id"), nullable=False),
        sa.Column(
            "modifier_option_id",
            sa.String(36),
            sa.ForeignKey("modifier_options.id"),
            nullable=False,
        ),
        sa.Column("modifier_name_snapshot", sa.String(255), nullable=False),
        sa.Column("extra_price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
    )

    # ------------------------------------------------------------------
    # qr_codes
    # ------------------------------------------------------------------
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("code_type", sa.String(20), nullable=False, server_default="store"),
        sa.Column("target_url", sa.String(500), nullable=False),
        sa.Column("table_number", sa.String(20), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # business_settings
    # ------------------------------------------------------------------
    op.create_table(
        "business_settings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("branch_id", sa.String(36), sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("service_mode", sa.String(20), nullable=False, server_default="both"),
        sa.Column("accepts_orders", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("opening_hours_json", sa.Text(), nullable=True),
        sa.Column("theme_json", sa.Text(), nullable=True),
    )

    # ------------------------------------------------------------------
    # event_logs
    # ------------------------------------------------------------------
    op.create_table(
        "event_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=True),
        sa.Column("event_name", sa.String(100), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("event_logs")
    op.drop_table("business_settings")
    op.drop_table("qr_codes")
    op.drop_table("order_item_modifiers")
    op.drop_table("order_items")
    op.drop_index("ix_orders_tenant_placed_at", table_name="orders")
    op.drop_index("ix_orders_tenant_status", table_name="orders")
    op.drop_table("orders")
    op.drop_table("product_modifier_groups")
    op.drop_table("modifier_options")
    op.drop_table("modifier_groups")
    op.drop_table("product_tags")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_table("branches")
    op.drop_index("ix_tenants_slug", table_name="tenants")
    op.drop_table("tenants")
