
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Category, CategorizationRule, Transaction
from schemas import CategoryCreate, CategorizationRuleCreate, TransactionCreate

# Assuming app is imported from main and get_db from database
# These will be mocked by conftest.py

def test_create_category(client: TestClient, session: Session):
    response = client.post(
        "/categories/",
        json={"category_name": "Shopping", "description": "General shopping expenses"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category_name"] == "Shopping"
    assert "category_id" in data

    category = session.query(Category).filter(Category.category_name == "Shopping").first()
    assert category is not None
    assert category.description == "General shopping expenses"

def test_create_categorization_rule(client: TestClient, session: Session):
    # First, create a category
    category_response = client.post(
        "/categories/",
        json={"category_name": "Bills", "description": "Utility bills"}
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["category_id"]

    # Then, create a rule using that category
    rule_response = client.post(
        "/rules/",
        json={
            "merchant_pattern": "Comcast",
            "category_id": category_id,
            "priority": 1
        }
    )
    assert rule_response.status_code == 200
    rule_data = rule_response.json()
    assert rule_data["merchant_pattern"] == "Comcast"
    assert rule_data["category_id"] == category_id
    assert "rule_id" in rule_data

    rule = session.query(CategorizationRule).filter(CategorizationRule.merchant_pattern == "Comcast").first()
    assert rule is not None
    assert rule.priority == 1

def test_categorize_transaction_amazon_shopping(client: TestClient, session: Session):
    # Setup: Create Shopping category and Amazon rule
    shopping_category_response = client.post(
        "/categories/",
        json={"category_name": "Shopping", "description": "General shopping expenses"}
    )
    shopping_category_id = shopping_category_response.json()["category_id"]
    client.post(
        "/rules/",
        json={
            "merchant_pattern": "Amazon",
            "category_id": shopping_category_id,
            "priority": 1
        }
    )

    # Test: Categorize a transaction from Amazon
    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext123",
            "merchant_name": "Amazon.com",
            "amount": 50.00,
            "date": "2023-01-01",
            "description": "Kindle purchase"
        }
    )
    assert transaction_response.status_code == 200
    transaction_data = transaction_response.json()
    assert transaction_data["merchant_name"] == "Amazon.com"
    assert transaction_data["assigned_category"]["category_name"] == "Shopping"
    assert transaction_data["flagged_for_review"] is False

def test_categorize_transaction_comcast_bills(client: TestClient, session: Session):
    # Setup: Create Bills category and Comcast rule
    bills_category_response = client.post(
        "/categories/",
        json={"category_name": "Bills", "description": "Utility bills"}
    )
    bills_category_id = bills_category_response.json()["category_id"]
    client.post(
        "/rules/",
        json={
            "merchant_pattern": "Comcast",
            "category_id": bills_category_id,
            "priority": 1
        }
    )

    # Test: Categorize a transaction from Comcast
    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext124",
            "merchant_name": "Comcast Cable",
            "amount": 100.00,
            "date": "2023-01-02",
            "description": "Internet bill"
        }
    )
    assert transaction_response.status_code == 200
    transaction_data = transaction_response.json()
    assert transaction_data["merchant_name"] == "Comcast Cable"
    assert transaction_data["assigned_category"]["category_name"] == "Bills"
    assert transaction_data["flagged_for_review"] is False

def test_categorize_transaction_unknown_merchant_flagged(client: TestClient, session: Session):
    # No rule for 'Unknown Merchant'
    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext125",
            "merchant_name": "Unknown Merchant XYZ",
            "amount": 25.00,
            "date": "2023-01-03",
            "description": "Random purchase"
        }
    )
    assert transaction_response.status_code == 200
    transaction_data = transaction_response.json()
    assert transaction_data["merchant_name"] == "Unknown Merchant XYZ"
    assert transaction_data["assigned_category"] is None
    assert transaction_data["flagged_for_review"] is True

def test_categorize_transaction_unknown_merchant_no_catch_all_flagged(client: TestClient, session: Session):
    # Setup: Ensure no catch-all rule exists that would prevent flagging.
    # We are explicitly NOT creating a rule with merchant_pattern: "%" here.
    # Also, ensure no specific rule for "Walmart" exists for this test.

    # Test: Categorize a transaction from an unknown merchant (e.g., "Walmart Supercenter")
    # without any specific or catch-all rules.
    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext126",
            "merchant_name": "Walmart Supercenter",
            "amount": 75.00,
            "date": "2023-01-04",
            "description": "Groceries and household items"
        }
    )
    assert transaction_response.status_code == 200
    transaction_data = transaction_response.json()
    assert transaction_data["merchant_name"] == "Walmart Supercenter"
    assert transaction_data["assigned_category"] is None  # Should be None as no rule matched
    assert transaction_data["flagged_for_review"] is True # Should be flagged for review

def test_get_transactions(client: TestClient, session: Session):
    # Setup: Create a category and a transaction
    category_response = client.post(
        "/categories/",
        json={"category_name": "Travel", "description": "Travel expenses"}
    )
    travel_category_id = category_response.json()["category_id"]

    client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext127",
            "merchant_name": "Delta Airlines",
            "amount": 300.00,
            "date": "2023-01-05",
            "description": "Flight ticket",
            "assigned_category_id": travel_category_id # Manually assign for this test
        }
    )

    response = client.get("/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(t["merchant_name"] == "Delta Airlines" for t in data)

def test_manual_recategorization(client: TestClient, session: Session):
    # Setup: Create categories and a transaction
    shopping_category_response = client.post(
        "/categories/",
        json={"category_name": "Shopping", "description": "General shopping expenses"}
    )
    shopping_category_id = shopping_category_response.json()["category_id"]

    food_category_response = client.post(
        "/categories/",
        json={"category_name": "Food", "description": "Food and dining"}
    )
    food_category_id = food_category_response.json()["category_id"]

    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext128",
            "merchant_name": "Local Cafe",
            "amount": 15.00,
            "date": "2023-01-06",
            "description": "Coffee and pastry",
            "assigned_category_id": shopping_category_id # Initially categorized as Shopping
        }
    )
    transaction_id = transaction_response.json()["transaction_id"]

    # Test: Re-categorize to Food
    update_response = client.put(
        f"/transactions/{transaction_id}/recategorize",
        json={
            "assigned_category_id": food_category_id
        }
    )
    assert update_response.status_code == 200
    updated_transaction = update_response.json()
    assert updated_transaction["assigned_category"]["category_name"] == "Food"
    assert updated_transaction["manual_override"] is True

def test_report_incorrect_categorization(client: TestClient, session: Session):
    # Setup: Create a transaction
    category_response = client.post(
        "/categories/",
        json={"category_name": "Entertainment", "description": "Movies, concerts, etc."}
    )
    entertainment_category_id = category_response.json()["category_id"]

    transaction_response = client.post(
        "/transactions/categorize",
        json={
            "external_id": "ext129",
            "merchant_name": "Netflix",
            "amount": 19.99,
            "date": "2023-01-07",
            "description": "Monthly subscription",
            "assigned_category_id": entertainment_category_id
        }
    )
    transaction_id = transaction_response.json()["transaction_id"]

    # Test: Report incorrect categorization
    report_response = client.post(
        f"/transactions/{transaction_id}/report",
        json={
            "reported_by_user_id": "user123",
            "issue_description": "Netflix should be Streaming, not Entertainment"
        }
    )
    assert report_response.status_code == 200
    reported_issue = report_response.json()
    assert reported_issue["transaction_id"] == transaction_id
    assert reported_issue["reported_by_user_id"] == "user123"
    assert reported_issue["status"] == "Open"
