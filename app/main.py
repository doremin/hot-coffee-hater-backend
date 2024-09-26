from fastapi import FastAPI
from app.routes import stores
from app.database import engine, Base

app = FastAPI()

# 데이터베이스 테이블 생성 (필요한 경우)
Base.metadata.create_all(bind=engine)

# 라우터 포함
app.include_router(stores.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)