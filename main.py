
from fastapi import FastAPI
from routers import loan_applications
from database import Base, engine

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(loan_applications.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Loan Application API"}
