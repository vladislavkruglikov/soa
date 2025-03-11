from fastapi import FastAPI
from user_service.database import Base, engine
from user_service.user_routes import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")
app.include_router(user_router, prefix="/users", tags=["Users"])