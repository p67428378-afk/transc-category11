
from fastapi import FastAPI
from database import Base, engine
from routers import transactions

app = FastAPI()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(transactions.router)
