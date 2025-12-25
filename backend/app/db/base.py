from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# NAMING CONVENTION (Crucial for Alembic)
# This ensures constraints have names like "pk_user" instead of "pk_user_29384"
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    # explicitly define metadata to inject the naming convention
    metadata = MetaData(naming_convention=naming_convention)
