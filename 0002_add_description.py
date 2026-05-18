"""add description to products

Revision ID: 0002_add_description
Revises: 0001_create_products
Create Date: 2025-01-01 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_description"
down_revision: Union[str, None] = "0001_create_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )
    op.execute("UPDATE products SET description='High-performance laptop' WHERE title='Laptop'")
    op.execute("UPDATE products SET description='Wireless optical mouse'  WHERE title='Mouse'")


def downgrade() -> None:
    op.drop_column("products", "description")
