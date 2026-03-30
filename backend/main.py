from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routers import custom_mappings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(custom_mappings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Transaction Categorization and Budget Update Service"}
