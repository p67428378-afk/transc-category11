from typing import Dict

class PremiumService:
    BASE_RATE = 500.0

    # Default mappings, these should ideally come from a configuration service or database
    VEHICLE_MULTIPLIERS: Dict[str, float] = {
        "Sedan": 1.0,
        "SUV": 1.2,
        "Truck": 1.4,
        "Motorcycle": 0.8,
        "Sports Car": 1.6,
    }

    NCB_DISCOUNTS: Dict[int, float] = {
        0: 0.0,   # 0 years no claims = 0% discount
        1: 0.20,  # 1 year no claims = 20% discount
        2: 0.25,  # 2 years no claims = 25% discount
        3: 0.30,  # 3 years no claims = 30% discount
        4: 0.40,  # 4 years no claims = 40% discount
        5: 0.50,  # 5+ years no claims = 50% discount (capped)
    }
    MAX_NCB_DISCOUNT = 0.50 # 50% cap

    def calculate_premium(self, vehicle_type: str, ncb_years: int) -> float:
        vehicle_multiplier = self.VEHICLE_MULTIPLIERS.get(vehicle_type, 1.0) # Default to 1.0 if type not found

        # Ensure ncb_years is not negative
        ncb_years = max(0, ncb_years)

        # Get NCB discount, capping at MAX_NCB_DISCOUNT
        # Find the highest NCB year less than or equal to ncb_years
        applicable_ncb_year = 0
        for year in sorted(self.NCB_DISCOUNTS.keys()):
            if ncb_years >= year:
                applicable_ncb_year = year
            else:
                break
        ncb_discount = self.NCB_DISCOUNTS.get(applicable_ncb_year, 0.0)

        ncb_discount = min(ncb_discount, self.MAX_NCB_DISCOUNT)

        # Calculate premium
        premium = (self.BASE_RATE * vehicle_multiplier) * (1 - ncb_discount)
        return round(premium, 2)
