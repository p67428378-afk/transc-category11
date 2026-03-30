from config import BASE_PREMIUM, NCB_DISCOUNTS, VEHICLE_MULTIPLIERS

def calculate_premium(vehicle_type: str, ncb_years: int) -> float:
    if ncb_years < 0:
        raise ValueError("NCB years cannot be negative")

    if vehicle_type not in VEHICLE_MULTIPLIERS:
        raise ValueError(f"Invalid vehicle type: {vehicle_type}")

    # Apply NCB discount
    ncb_discount_percentage = 0.0
    if ncb_years >= 4:
        ncb_discount_percentage = NCB_DISCOUNTS[4]
    else:
        ncb_discount_percentage = NCB_DISCOUNTS.get(ncb_years, 0.0)

    premium_after_ncb = BASE_PREMIUM * (1 - ncb_discount_percentage)

    # Apply vehicle type multiplier
    vehicle_multiplier = VEHICLE_MULTIPLIERS[vehicle_type]
    final_premium = premium_after_ncb * vehicle_multiplier

    return round(final_premium, 2)
