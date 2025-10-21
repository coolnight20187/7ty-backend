from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from . import models
from .routers import auth, admin, bills, transactions

from fastapi.middleware.cors import CORSMiddleware

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="7ty.vn API")

# Setup CORS
origins = [
    "http://localhost",
    "http://localhost:5173", # Cổng mặc định của Vite
    # Thêm các địa chỉ frontend khác nếu có
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(bills.router)
app.include_router(transactions.router)

@app.get("/")
def read_root():
    return {"Project": "7ty.vn"}

