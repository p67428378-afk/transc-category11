from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

BASE_PREMIUM = 500.00

NCB_DISCOUNTS = {
    0: 0.0,
    1: 0.2,
    2: 0.3,
    3: 0.4,
    4: 0.5, # Capped at 50%
}

VEHICLE_MULTIPLIERS = {
    "Motorcycle": 0.8,
    "Sedan": 1.0,
    "SUV": 1.2,
    "Sports Car": 1.6,
}
