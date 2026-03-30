from fastapi import FastAPI
from app.api.v1.endpoints import custom_mapping
from app.database import Base, engine

app = FastAPI()

# Database table creation should be handled by migrations or explicitly in a startup event.
# For testing, it's handled in conftest.py.
# Base.metadata.create_all(bind=engine)

app.include_router(custom_mapping.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Custom Mapping API"}
