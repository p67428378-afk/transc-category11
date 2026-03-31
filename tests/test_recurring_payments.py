from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import RecurringPayment, User, Frequency, RecurringPaymentStatus
from app.schemas.schemas import RecurringPaymentCreate, RecurringPaymentUpdate
from datetime import datetime, timedelta

def test_create_recurring_payment(client: TestClient, session: Session):
    # Create a dummy user
    user = User(email="test@example.com", account_id="ACC123")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Define a recurring payment to create
    start_date = datetime.now() + timedelta(days=1)
    recurring_payment_data = {
        "user_id": user.id,
        "biller_name": "Internet Provider",
        "amount": 50.0,
        "currency": "USD",
        "start_date": start_date.isoformat(),
        "frequency": Frequency.MONTHLY.value,
    }

    response = client.post("/api/v1/recurring-payments/", json=recurring_payment_data)

    assert response.status_code == 201  # Changed from 200 to 201
    data = response.json()
    assert data["biller_name"] == "Internet Provider"
    assert data["amount"] == 50.0
    assert data["user_id"] == user.id
    assert data["status"] == RecurringPaymentStatus.ACTIVE.value
    assert "id" in data
    assert "next_payment_date" in data

    # Verify the payment is in the database
    db_payment = session.query(RecurringPayment).filter(RecurringPayment.id == data["id"]).first()
    assert db_payment is not None
    assert db_payment.biller_name == "Internet Provider"

def test_read_recurring_payment(client: TestClient, session: Session):
    user = User(email="test_read@example.com", account_id="ACC124")
    session.add(user)
    session.commit()
    session.refresh(user)

    start_date = datetime.now() + timedelta(days=1)
    recurring_payment_create = RecurringPaymentCreate(
        user_id=user.id,
        biller_name="Electricity Bill",
        amount=100.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.MONTHLY
    )
    db_payment = RecurringPayment(
        **recurring_payment_create.model_dump(),
        next_payment_date=start_date + timedelta(days=30),
        status=RecurringPaymentStatus.ACTIVE
    )
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)

    response = client.get(f"/api/v1/recurring-payments/{db_payment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == db_payment.id
    assert data["biller_name"] == "Electricity Bill"

def test_read_recurring_payments_by_user(client: TestClient, session: Session):
    user = User(email="test_list@example.com", account_id="ACC125")
    session.add(user)
    session.commit()
    session.refresh(user)

    start_date = datetime.now() + timedelta(days=1)
    payment1 = RecurringPayment(
        user_id=user.id,
        biller_name="Rent",
        amount=1000.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.MONTHLY,
        next_payment_date=start_date + timedelta(days=30),
        status=RecurringPaymentStatus.ACTIVE
    )
    payment2 = RecurringPayment(
        user_id=user.id,
        biller_name="Gym Membership",
        amount=30.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.WEEKLY,
        next_payment_date=start_date + timedelta(weeks=1),
        status=RecurringPaymentStatus.ACTIVE
    )
    session.add_all([payment1, payment2])
    session.commit()
    session.refresh(payment1)
    session.refresh(payment2)

    response = client.get(f"/api/v1/recurring-payments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["biller_name"] == "Rent"
    assert data[1]["biller_name"] == "Gym Membership"

def test_update_recurring_payment(client: TestClient, session: Session):
    user = User(email="test_update@example.com", account_id="ACC126")
    session.add(user)
    session.commit()
    session.refresh(user)

    start_date = datetime.now() + timedelta(days=1)
    recurring_payment_create = RecurringPaymentCreate(
        user_id=user.id,
        biller_name="Old Biller",
        amount=10.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.WEEKLY
    )
    db_payment = RecurringPayment(
        **recurring_payment_create.model_dump(),
        next_payment_date=start_date + timedelta(weeks=1),
        status=RecurringPaymentStatus.ACTIVE
    )
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)

    update_data = {
        "biller_name": "New Biller",
        "amount": 20.0,
        "frequency": Frequency.MONTHLY.value
    }
    response = client.put(f"/api/v1/recurring-payments/{db_payment.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["biller_name"] == "New Biller"
    assert data["amount"] == 20.0
    assert data["frequency"] == Frequency.MONTHLY.value
    assert data["id"] == db_payment.id

    db_payment_updated = session.query(RecurringPayment).filter(RecurringPayment.id == db_payment.id).first()
    assert db_payment_updated.biller_name == "New Biller"
    assert db_payment_updated.amount == 20.0
    assert db_payment_updated.frequency == Frequency.MONTHLY

def test_delete_recurring_payment(client: TestClient, session: Session):
    user = User(email="test_delete@example.com", account_id="ACC127")
    session.add(user)
    session.commit()
    session.refresh(user)

    start_date = datetime.now() + timedelta(days=1)
    recurring_payment_create = RecurringPaymentCreate(
        user_id=user.id,
        biller_name="To Be Deleted",
        amount=5.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.WEEKLY
    )
    db_payment = RecurringPayment(
        **recurring_payment_create.model_dump(),
        next_payment_date=start_date + timedelta(weeks=1),
        status=RecurringPaymentStatus.ACTIVE
    )
    session.add(db_payment)
    session.commit()
    session.refresh(db_payment)

    response = client.delete(f"/api/v1/recurring-payments/{db_payment.id}")
    assert response.status_code == 204

    db_payment_deleted = session.query(RecurringPayment).filter(RecurringPayment.id == db_payment.id).first()
    assert db_payment_deleted is None

def test_create_recurring_payment_past_start_date(client: TestClient, session: Session):
    user = User(email="test_past_date@example.com", account_id="ACC128")
    session.add(user)
    session.commit()
    session.refresh(user)

    past_start_date = datetime.now() - timedelta(days=1)
    recurring_payment_data = {
        "user_id": user.id,
        "biller_name": "Past Date Payment",
        "amount": 10.0,
        "currency": "USD",
        "start_date": past_start_date.isoformat(),
        "frequency": Frequency.MONTHLY.value,
    }

    response = client.post("/api/v1/recurring-payments/", json=recurring_payment_data)
    assert response.status_code == 400
    assert "Start date cannot be in the past" in response.json()["detail"]

def test_unauthorized_access_to_payment(client: TestClient, session: Session):
    # Create user 1 and their payment
    user1 = User(email="user1@example.com", account_id="ACC129")
    session.add(user1)
    session.commit()
    session.refresh(user1)

    start_date = datetime.now() + timedelta(days=1)
    payment_user1 = RecurringPayment(
        user_id=user1.id,
        biller_name="User1 Payment",
        amount=100.0,
        currency="USD",
        start_date=start_date,
        frequency=Frequency.MONTHLY,
        next_payment_date=start_date + timedelta(days=30),
        status=RecurringPaymentStatus.ACTIVE
    )
    session.add(payment_user1)
    session.commit()
    session.refresh(payment_user1)

    # Create user 2 (who will try to access user 1's payment)
    user2 = User(email="user2@example.com", account_id="ACC130")
    session.add(user2)
    session.commit()
    session.refresh(user2)

    # Temporarily override get_current_user to return user2
    # This is a simplified way for testing; real auth would be more complex
    from app.api.v1.endpoints.recurring_payments import get_current_user
    def override_get_current_user_for_user2():
        return user2
    client.app.dependency_overrides[get_current_user] = override_get_current_user_for_user2

    # User 2 tries to read user 1's payment
    response = client.get(f"/api/v1/recurring-payments/{payment_user1.id}")
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

    # User 2 tries to update user 1's payment
    response = client.put(f"/api/v1/recurring-payments/{payment_user1.id}", json={"amount": 200.0})
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

    # User 2 tries to delete user 1's payment
    response = client.delete(f"/api/v1/recurring-payments/{payment_user1.id}")
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

    # Clean up override
    client.app.dependency_overrides.pop(get_current_user)
