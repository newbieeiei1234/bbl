from db.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Bookings(Base):
    __tablename__ = "Bookings"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    start_time = Column("start_time", String, nullable=False)
    end_time = Column("end_time", String, nullable=False)
    name = Column("name", String, nullable=False)
    detail = Column("detail", String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("Users.id"), nullable=False)