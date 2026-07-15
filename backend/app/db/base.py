from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for future persistence models."""


# Import models here so Alembic receives complete metadata.
from app.models import auth, organization  # noqa: E402, F401
