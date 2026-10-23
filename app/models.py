from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class EMIRequest(BaseModel):
    loan_amount: float = Field(
        ...,
        gt=0,
        description="Principal loan amount in currency units (e.g. 500000)",
        examples=[500000.0],
    )
    annual_interest_rate: float = Field(
        ...,
        ge=0,
        description="Annual interest rate percentage (e.g. 8.5 for 8.5%)",
        examples=[8.5],
    )
    tenure_months: Optional[int] = Field(
        None,
        gt=0,
        description="Loan tenure in months (e.g. 36 for 3 years)",
        examples=[36],
    )
    tenure_years: Optional[float] = Field(
        None,
        gt=0,
        description="Loan tenure in years (e.g. 3 for 3 years)",
        examples=[3.0],
    )
    include_schedule: bool = Field(
        default=False,
        description="Include full monthly amortization schedule in the response",
    )

    @model_validator(mode="after")
    def validate_and_compute_tenure(self) -> "EMIRequest":
        if self.tenure_months is None and self.tenure_years is None:
            raise ValueError("Either 'tenure_months' or 'tenure_years' must be provided.")
        if self.tenure_months is None and self.tenure_years is not None:
            self.tenure_months = int(round(self.tenure_years * 12))
        return self


class MonthlyBreakdown(BaseModel):
    month: int = Field(..., description="Installment month number (1 to N)")
    beginning_balance: float = Field(..., description="Outstanding balance before monthly payment")
    emi: float = Field(..., description="Total installment amount paid this month")
    principal_paid: float = Field(..., description="Portion of EMI going towards principal reduction")
    interest_paid: float = Field(..., description="Portion of EMI going towards interest charge")
    ending_balance: float = Field(..., description="Remaining balance after payment")


class EMIResponse(BaseModel):
    loan_amount: float = Field(..., description="Principal loan amount")
    annual_interest_rate: float = Field(..., description="Annual interest rate in percentage")
    tenure_months: int = Field(..., description="Tenure in months")
    tenure_years: float = Field(..., description="Tenure in years")
    monthly_emi: float = Field(..., description="Equated Monthly Installment amount")
    total_interest: float = Field(..., description="Total interest paid over the loan duration")
    total_payment: float = Field(..., description="Total amount paid (Principal + Interest)")
    schedule: Optional[List[MonthlyBreakdown]] = Field(
        default=None,
        description="Month-by-month amortization schedule (if requested)",
    )


class LoanComparisonItem(BaseModel):
    loan_amount: float = Field(..., gt=0, examples=[500000.0])
    annual_interest_rate: float = Field(..., ge=0, examples=[8.5])
    tenure_months: int = Field(..., gt=0, examples=[36])
    label: Optional[str] = Field(None, examples=["Bank A - 3 Year Plan"])


class LoanComparisonRequest(BaseModel):
    offers: List[LoanComparisonItem] = Field(..., min_length=2, max_length=10)


class LoanComparisonResult(BaseModel):
    label: str
    loan_amount: float
    annual_interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payment: float


class LoanComparisonResponse(BaseModel):
    results: List[LoanComparisonResult]
    lowest_emi_offer: str
    lowest_total_interest_offer: str
