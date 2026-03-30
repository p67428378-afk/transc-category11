from fastapi import FastAPI
from routers import premiums
from database import engine, Base

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(premiums.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vehicle Insurance Premium Calculator API"}
