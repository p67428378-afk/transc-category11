from fastapi import FastAPI
from database import engine, Base
from routers import custom_mapping, transactions

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(custom_mapping.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Transaction Categorization and Budget Update Service"}
