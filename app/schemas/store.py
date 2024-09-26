from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from geoalchemy2.functions import ST_AsText

from sqlalchemy.orm import Session
from uuid import UUID

class StoreBase(BaseModel):
    name: str
    address: str
    zip_code: str
    americano: Dict[str, int]
    menu_items: Dict[str, int]

class StoreInDB(StoreBase):
    id: UUID

    class Config:
        orm_mode = True

class MenuItemInfo(BaseModel):
    name: str
    price: int

class StoreDTO(StoreInDB):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance: Optional[float] = None

    @classmethod
    def from_orm(cls, store_data, db: Session):
        store, distance = store_data

        # geom 필드를 텍스트로 변환
        geom_text = db.scalar(ST_AsText(store.geom))

        # 위도와 경도 추출
        latitude = None
        longitude = None
        if geom_text:
            # WKT 형식의 POINT(longitude latitude)에서 좌표 추출
            coordinates = geom_text.split('(')[1].split(')')[0].split()
            longitude, latitude = map(float, coordinates)

        return cls(
            id=store.id,
            name=store.name,
            address=store.address,
            zip_code=store.zip_code,
            americano=store.americano,
            menu_items=store.menu_items,
            latitude=latitude,
            longitude=longitude,
            distance=distance
        )

    def get_formatted_americano(self) -> Dict[str, MenuItemInfo]:
        formatted_response = {}

        for key, value in self.americano.items():
            formatted_response["americano"] = MenuItemInfo(
                name=key,
                price=value,
            )

        return formatted_response

    def get_formatted_menu_items(self) -> Dict[str, List[MenuItemInfo]]:
        return {
            "menu_items": [
                MenuItemInfo(name=name, price=price)
                for name, price in self.menu_items.items()
            ]
        }

    def get_formatted_response(self) -> Dict:
        response = self.dict(exclude={'americano', 'menu_items'})
        response.update(self.get_formatted_americano())
        response.update(self.get_formatted_menu_items())
        return response

    class Config:
        orm_mode = True
        json_encoders = {
            UUID: lambda v: str(v)  # UUID를 문자열로 변환
        }

class FormattedStoreResponse(BaseModel):
    id: UUID
    name: str
    address: str
    zip_code: str
    latitude: float
    longitude: float
    distance: float
    americano: MenuItemInfo
    menu_items: List[MenuItemInfo]

    class Config:
        orm_mode = True