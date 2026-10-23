import math
from typing import List, Tuple
from app.models import (
    EMIResponse,
    MonthlyBreakdown,
    LoanComparisonItem,
    LoanComparisonResponse,
    LoanComparisonResult,
)


def compute_monthly_emi(loan_amount: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate the monthly EMI given principal, annual rate percentage, and tenure in months.
    Formula:
      EMI = [P x r x (1 + r)^n] / [(1 + r)^n - 1]
      where r = annual_rate / (12 * 100)
    If rate is 0%, EMI = P / n
    """
    if tenure_months <= 0:
        raise ValueError("Tenure months must be greater than zero.")
    if loan_amount <= 0:
        raise ValueError("Loan amount must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")

    if annual_rate == 0:
        return round(loan_amount / tenure_months, 2)

    monthly_rate = annual_rate / (12 * 100)
    factor = math.pow(1 + monthly_rate, tenure_months)
    emi = (loan_amount * monthly_rate * factor) / (factor - 1)
    return round(emi, 2)


def generate_amortization_schedule(
    loan_amount: float, annual_rate: float, tenure_months: int, monthly_emi: float
) -> Tuple[List[MonthlyBreakdown], float, float]:
    """
    Generate month-by-month amortization breakdown.
    Returns:
      (schedule, actual_total_payment, actual_total_interest)
    """
    monthly_rate = (annual_rate / (12 * 100)) if annual_rate > 0 else 0.0
    schedule: List[MonthlyBreakdown] = []
    balance = loan_amount

    total_interest_paid = 0.0
    total_payment = 0.0

    for month in range(1, tenure_months + 1):
        beginning_balance = round(balance, 2)
        interest_charge = round(beginning_balance * monthly_rate, 2)

        if month == tenure_months or beginning_balance <= 0:
            # Final month adjustments to close out loan accurately
            principal_portion = beginning_balance
            month_emi = round(principal_portion + interest_charge, 2)
            ending_balance = 0.0
        else:
            principal_portion = round(monthly_emi - interest_charge, 2)
            if principal_portion >= beginning_balance:
                principal_portion = beginning_balance
                month_emi = round(principal_portion + interest_charge, 2)
                ending_balance = 0.0
            else:
                ending_balance = round(beginning_balance - principal_portion, 2)
                month_emi = monthly_emi

        balance = ending_balance
        total_interest_paid += interest_charge
        total_payment += month_emi

        schedule.append(
            MonthlyBreakdown(
                month=month,
                beginning_balance=beginning_balance,
                emi=month_emi,
                principal_paid=principal_portion,
                interest_paid=interest_charge,
                ending_balance=ending_balance,
            )
        )

        if balance <= 0:
            break

    return schedule, round(total_payment, 2), round(total_interest_paid, 2)


def calculate_emi_details(
    loan_amount: float,
    annual_rate: float,
    tenure_months: int,
    include_schedule: bool = False,
) -> EMIResponse:
    """
    Compute full EMI details, interest, total payment, and optionally schedule.
    """
    monthly_emi = compute_monthly_emi(loan_amount, annual_rate, tenure_months)

    if include_schedule:
        schedule, total_payment, total_interest = generate_amortization_schedule(
            loan_amount, annual_rate, tenure_months, monthly_emi
        )
    else:
        schedule = None
        total_payment = round(monthly_emi * tenure_months, 2)
        total_interest = round(total_payment - loan_amount, 2)

    return EMIResponse(
        loan_amount=round(loan_amount, 2),
        annual_interest_rate=round(annual_rate, 2),
        tenure_months=tenure_months,
        tenure_years=round(tenure_months / 12, 2),
        monthly_emi=monthly_emi,
        total_interest=total_interest,
        total_payment=total_payment,
        schedule=schedule,
    )


def compare_loan_offers(offers: List[LoanComparisonItem]) -> LoanComparisonResponse:
    """
    Compare multiple loan offers to find lowest EMI and lowest total interest.
    """
    results: List[LoanComparisonResult] = []

    for idx, offer in enumerate(offers):
        label = offer.label or f"Offer {idx + 1}"
        emi = compute_monthly_emi(offer.loan_amount, offer.annual_interest_rate, offer.tenure_months)
        total_payment = round(emi * offer.tenure_months, 2)
        total_interest = round(total_payment - offer.loan_amount, 2)

        results.append(
            LoanComparisonResult(
                label=label,
                loan_amount=round(offer.loan_amount, 2),
                annual_interest_rate=round(offer.annual_interest_rate, 2),
                tenure_months=offer.tenure_months,
                monthly_emi=emi,
                total_interest=total_interest,
                total_payment=total_payment,
            )
        )

    lowest_emi_offer = min(results, key=lambda r: r.monthly_emi).label
    lowest_interest_offer = min(results, key=lambda r: r.total_interest).label

    return LoanComparisonResponse(
        results=results,
        lowest_emi_offer=lowest_emi_offer,
        lowest_total_interest_offer=lowest_interest_offer,
    )
