"""create products table

Revision ID: 0001_create_products
Revises: 
Create Date: 2025-01-01 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_products"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id",    sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(255),   nullable=False),
        sa.Column("price", sa.Float(),       nullable=False),
        sa.Column("count", sa.Integer(),     nullable=False, server_default="0"),
    )
    # Тестовые записи
    op.execute(
        "INSERT INTO products (title, price, count) VALUES "
        "('Laptop', 999.99, 10), "
        "('Mouse', 29.99, 50)"
    )


def downgrade() -> None:
    op.drop_table("products")
