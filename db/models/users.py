from db.models.base import Base
from sqlalchemy import Column, Integer, String, UniqueConstraint, Bool

class Users(Base):
    __tablename__ = "Users"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String(20), unique=True, nullable=False)
    hashed_password = Column("hashed_password", String, nullable=False)
    admin_status = Column("admin_status", Bool, nullable=False)

    __table_args__ = (
        UniqueConstraint("username", name="unique_username"),
    )