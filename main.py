from fastapi import FastAPI
from database import engine, Base

# Import models to ensure they are registered with SQLAlchemy Base
import models

app = FastAPI(
    title="Transaction Categorization Service",
    description="API for automatic transaction categorization and budget updates.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include routers here once they are created
from routers import mapping_router
app.include_router(mapping_router.router)
