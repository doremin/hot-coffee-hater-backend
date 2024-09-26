from sqlalchemy import Column, String, JSON
from geoalchemy2 import Geometry
from app.database import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    americano = Column(JSON)
    menu_items = Column(JSON)
    geom = Column(Geometry('POINT', srid=4326))

    def __repr__(self):
        return f"<Store(id={self.id}, name={self.name})>"
