from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class which provides automated table name
    and other utility methods."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
