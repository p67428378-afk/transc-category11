
from fastapi import FastAPI
from app.api.endpoints import kyc_router
from app.db.database import engine, Base

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KYC Onboarding Microservice",
    description="API for submitting and managing KYC details",
    version="1.0.0",
)

app.include_router(kyc_router.router, prefix="/api/v1", tags=["KYC"])
