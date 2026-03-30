import pytest
from services.premium_calculator import calculate_premium
from config import BASE_PREMIUM, NCB_DISCOUNTS, VEHICLE_MULTIPLIERS

def test_calculate_premium_no_ncb_sedan():
    # 0 years NCB, Sedan (1.0x multiplier)
    vehicle_type = "Sedan"
    ncb_years = 0
    expected_premium = BASE_PREMIUM * (1 - NCB_DISCOUNTS[0]) * VEHICLE_MULTIPLIERS["Sedan"]
    assert calculate_premium(vehicle_type, ncb_years) == expected_premium

def test_calculate_premium_1_year_ncb_sedan():
    # 1 year NCB, Sedan (1.0x multiplier)
    vehicle_type = "Sedan"
    ncb_years = 1
    expected_premium = BASE_PREMIUM * (1 - NCB_DISCOUNTS[1]) * VEHICLE_MULTIPLIERS["Sedan"]
    assert calculate_premium(vehicle_type, ncb_years) == expected_premium

def test_calculate_premium_4_years_ncb_motorcycle():
    # 4+ years NCB (capped at 50%), Motorcycle (0.8x multiplier)
    vehicle_type = "Motorcycle"
    ncb_years = 4
    expected_premium = BASE_PREMIUM * (1 - NCB_DISCOUNTS[4]) * VEHICLE_MULTIPLIERS["Motorcycle"]
    assert calculate_premium(vehicle_type, ncb_years) == expected_premium

def test_calculate_premium_5_years_ncb_suv():
    # 5 years NCB (capped at 50%), SUV (1.2x multiplier)
    vehicle_type = "SUV"
    ncb_years = 5 # Should be capped at 4 years NCB discount
    expected_premium = BASE_PREMIUM * (1 - NCB_DISCOUNTS[4]) * VEHICLE_MULTIPLIERS["SUV"]
    assert calculate_premium(vehicle_type, ncb_years) == expected_premium

def test_calculate_premium_invalid_vehicle_type():
    # Invalid vehicle type should raise ValueError
    vehicle_type = "Truck"
    ncb_years = 1
    with pytest.raises(ValueError, match="Invalid vehicle type"):
        calculate_premium(vehicle_type, ncb_years)

def test_calculate_premium_negative_ncb_years():
    # Negative NCB years should raise ValueError
    vehicle_type = "Sedan"
    ncb_years = -1
    with pytest.raises(ValueError, match="NCB years cannot be negative"):
        calculate_premium(vehicle_type, ncb_years)
