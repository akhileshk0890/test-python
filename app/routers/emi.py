from fastapi import APIRouter, HTTPException, Query, status
from app.models import (
    EMIRequest,
    EMIResponse,
    LoanComparisonRequest,
    LoanComparisonResponse,
)
from app.services.emi_calculator import (
    calculate_emi_details,
    compare_loan_offers,
)

router = APIRouter(prefix="/api/v1/emi", tags=["EMI Calculator"])


@router.post(
    "/calculate",
    response_model=EMIResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Loan EMI & Summary",
    description=(
        "Calculate Equated Monthly Installment (EMI), total interest payable, "
        "and total amount. Optionally include month-by-month amortization schedule."
    ),
)
def calculate_emi_endpoint(payload: EMIRequest) -> EMIResponse:
    try:
        tenure_months = payload.tenure_months
        assert tenure_months is not None  # Guaranteed by EMIRequest model validator
        return calculate_emi_details(
            loan_amount=payload.loan_amount,
            annual_rate=payload.annual_interest_rate,
            tenure_months=tenure_months,
            include_schedule=payload.include_schedule,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/quick",
    response_model=EMIResponse,
    status_code=status.HTTP_200_OK,
    summary="Quick EMI calculation via Query Parameters",
    description="Convenient GET endpoint for quick calculation directly from the browser URL.",
)
def quick_calculate_endpoint(
    loan_amount: float = Query(
        ..., gt=0, description="Principal loan amount", examples=[500000.0]
    ),
    annual_interest_rate: float = Query(
        ..., ge=0, description="Annual interest rate percentage", examples=[8.5]
    ),
    tenure_months: int = Query(
        ..., gt=0, description="Tenure in months", examples=[36]
    ),
    include_schedule: bool = Query(
        False, description="Include amortization breakdown"
    ),
) -> EMIResponse:
    try:
        return calculate_emi_details(
            loan_amount=loan_amount,
            annual_rate=annual_interest_rate,
            tenure_months=tenure_months,
            include_schedule=include_schedule,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/compare",
    response_model=LoanComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Multiple Loan Offers",
    description="Compare different interest rates and tenures to find the optimal EMI and lowest total cost.",
)
def compare_loans_endpoint(payload: LoanComparisonRequest) -> LoanComparisonResponse:
    try:
        return compare_loan_offers(payload.offers)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
