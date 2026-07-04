from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth.auth import router as authRouter
from api.booking.router import router as bookingRouter
from db.models.base import Base
from db.db_connection import engine

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"]
)

app.include_router(authRouter)
app.include_router(bookingRouter)