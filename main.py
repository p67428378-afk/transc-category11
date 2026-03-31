from fastapi import FastAPI
from database import engine, Base
from routers import custom_mapping, transactions

app = FastAPI()

# Removed on_startup event that creates tables, as this is handled by test fixtures for testing
# and should be handled by alembic migrations in production.
# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)

app.include_router(custom_mapping.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Transaction Categorization and Budget Update Service"}
