import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.emi_calculator import (
    compute_monthly_emi,
    generate_amortization_schedule,
)

client = TestClient(app)


def test_compute_monthly_emi_zero_interest():
    # 12,000 loan over 12 months at 0% interest -> 1,000 / month
    emi = compute_monthly_emi(loan_amount=12000.0, annual_rate=0.0, tenure_months=12)
    assert emi == 1000.0


def test_compute_monthly_emi_standard():
    # 100,000 at 10% annual interest for 12 months
    # Formula check: monthly rate = 10 / 1200 = 0.008333333
    # EMI ~ 8791.59
    emi = compute_monthly_emi(loan_amount=100000.0, annual_rate=10.0, tenure_months=12)
    assert pytest.approx(emi, 0.05) == 8791.59


def test_generate_amortization_schedule():
    loan_amount = 50000.0
    annual_rate = 12.0
    tenure_months = 6
    emi = compute_monthly_emi(loan_amount, annual_rate, tenure_months)

    schedule, total_payment, total_interest = generate_amortization_schedule(
        loan_amount, annual_rate, tenure_months, emi
    )

    assert len(schedule) == 6
    assert schedule[-1].ending_balance == 0.0

    # Total principal paid across schedule must equal original principal
    total_principal_paid = sum(item.principal_paid for item in schedule)
    assert pytest.approx(total_principal_paid, 0.1) == loan_amount


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Loan EMI Calculator API"
    assert "documentation" in data


def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_calculate_endpoint_with_months():
    payload = {
        "loan_amount": 500000,
        "annual_interest_rate": 8.5,
        "tenure_months": 36,
        "include_schedule": False,
    }
    response = client.post("/api/v1/emi/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["loan_amount"] == 500000.0
    assert data["monthly_emi"] > 0
    assert data["total_interest"] > 0
    assert data["total_payment"] == pytest.approx(
        data["loan_amount"] + data["total_interest"], 0.1
    )
    assert data["schedule"] is None


def test_calculate_endpoint_with_years():
    payload = {
        "loan_amount": 100000,
        "annual_interest_rate": 7.0,
        "tenure_years": 2,
        "include_schedule": True,
    }
    response = client.post("/api/v1/emi/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tenure_months"] == 24
    assert len(data["schedule"]) == 24
    assert data["schedule"][-1]["ending_balance"] == 0.0


def test_quick_calculate_endpoint():
    response = client.get(
        "/api/v1/emi/quick?loan_amount=200000&annual_interest_rate=9.0&tenure_months=24"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monthly_emi"] > 0
    assert data["tenure_months"] == 24


def test_compare_endpoint():
    payload = {
        "offers": [
            {
                "label": "Bank A - 3 Years",
                "loan_amount": 500000,
                "annual_interest_rate": 8.5,
                "tenure_months": 36,
            },
            {
                "label": "Bank B - 5 Years",
                "loan_amount": 500000,
                "annual_interest_rate": 9.0,
                "tenure_months": 60,
            },
        ]
    }
    response = client.post("/api/v1/emi/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    # Longer tenure typically yields lower monthly EMI but higher total interest
    assert data["lowest_emi_offer"] == "Bank B - 5 Years"
    assert data["lowest_total_interest_offer"] == "Bank A - 3 Years"


def test_invalid_input_validation():
    # Negative loan amount should fail validation (HTTP 422)
    response = client.post(
        "/api/v1/emi/calculate",
        json={"loan_amount": -1000, "annual_interest_rate": 5, "tenure_months": 12},
    )
    assert response.status_code == 422
