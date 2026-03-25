from fastapi import FastAPI
from app.routers import loan_application
from app.database import Base, engine

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

app.include_router(loan_application.router)
