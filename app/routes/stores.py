from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.store import Store
from app.schemas.store import StoreDTO, FormattedStoreResponse
from geoalchemy2.functions import ST_Distance, ST_SetSRID, ST_MakePoint


router = APIRouter()


@router.get("/stores", response_model=List[FormattedStoreResponse])
def get_nearest_stores(
        latitude: float = Query(..., description="User's latitude"),
        longitude: float = Query(..., description="User's longitude"),
        db: Session = Depends(get_db)
):
    # 사용자 위치 포인트 생성
    user_location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

    # 거리 계산 및 가장 가까운 20개 매장 선택
    stores = db.query(Store, ST_Distance(Store.geom, user_location).label('distance')).order_by(
        ST_Distance(Store.geom, user_location)
    ).limit(20).all()

    # DTO로 변환
    store_dtos = [StoreDTO.from_orm(store, db) for store in stores]

    # 포맷팅된 응답 생성 및 아메리카노 가격으로 정렬 (같은 가격이면 가까운 순)
    formatted_responses = [dto.get_formatted_response() for dto in store_dtos]
    formatted_responses.sort(key=lambda x: (x["americano"].price, x['distance']))

    return formatted_responses