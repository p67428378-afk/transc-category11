from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.v1.endpoints import recurring_payments

# Import models to ensure they are registered with SQLAlchemy Base
from app.models import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recurring Payments API",
    description="API for managing recurring payments, balance checks, and notifications.",
    version="1.0.0",
)

app.include_router(recurring_payments.router, prefix="/api/v1", tags=["Recurring Payments"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Recurring Payments API"}
