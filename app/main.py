from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import kyc
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="KYC Onboarding Microservice", lifespan=lifespan)

app.include_router(kyc.router, prefix="/api/v1", tags=["kyc"])
