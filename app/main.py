from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.routers import emi

app = FastAPI(
    title="Loan EMI Calculator API",
    description=(
        "Production-ready FastAPI service to calculate Equated Monthly Installment (EMI), "
        "amortization schedules, and compare multiple loan options."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local frontends / web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include EMI Routers
app.include_router(emi.router)


@app.get("/", summary="Root API Information", tags=["General"])
def root():
    return {
        "service": "Loan EMI Calculator API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "calculate_emi": "POST /api/v1/emi/calculate",
            "quick_calculate": "GET /api/v1/emi/quick?loan_amount=500000&annual_interest_rate=8.5&tenure_months=36",
            "compare_offers": "POST /api/v1/emi/compare",
            "interactive_ui": "/ui",
        },
    }


@app.get("/health", summary="Health Check", tags=["General"])
def health_check():
    return {"status": "healthy"}


@app.get("/ui", response_class=HTMLResponse, summary="Interactive UI", tags=["UI"])
def interactive_ui():
    """Simple embedded client to test the EMI API directly in the browser."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EMI Calculator</title>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0ea5e9;
      --border: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; max-width: 520px; width: 100%; padding: 28px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    h1 { font-size: 24px; margin-bottom: 8px; color: var(--accent); }
    p.sub { color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }
    .form-group { margin-bottom: 16px; }
    label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px; color: var(--text-muted); }
    input[type="number"] { width: 100%; padding: 10px 12px; background: #0b1120; border: 1px solid var(--border); border-radius: 6px; color: white; font-size: 15px; }
    input[type="checkbox"] { margin-right: 8px; }
    button { width: 100%; padding: 12px; background: var(--accent); color: #0f172a; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.2s; margin-top: 8px; }
    button:hover { background: var(--accent-hover); }
    .result { margin-top: 24px; padding: 16px; background: #0b1120; border-radius: 8px; border: 1px solid var(--border); display: none; }
    .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
    .stat-row:last-child { border-bottom: none; }
    .stat-value { font-weight: bold; color: var(--accent); }
  </style>
</head>
<body>
  <div class="card">
    <h1>EMI Calculator</h1>
    <p class="sub">Powered by FastAPI backend (/api/v1/emi/calculate)</p>
    <div class="form-group">
      <label for="amount">Loan Amount</label>
      <input type="number" id="amount" value="500000" step="1000">
    </div>
    <div class="form-group">
      <label for="rate">Annual Interest Rate (%)</label>
      <input type="number" id="rate" value="8.5" step="0.1">
    </div>
    <div class="form-group">
      <label for="tenure">Tenure (Months)</label>
      <input type="number" id="tenure" value="36" step="1">
    </div>
    <button onclick="calculate()">Calculate EMI</button>

    <div class="result" id="result-box">
      <div class="stat-row">
        <span>Monthly EMI</span>
        <span class="stat-value" id="val-emi">-</span>
      </div>
      <div class="stat-row">
        <span>Total Interest</span>
        <span class="stat-value" id="val-interest">-</span>
      </div>
      <div class="stat-row">
        <span>Total Payment</span>
        <span class="stat-value" id="val-total">-</span>
      </div>
    </div>
  </div>

  <script>
    async function calculate() {
      const amount = parseFloat(document.getElementById('amount').value);
      const rate = parseFloat(document.getElementById('rate').value);
      const tenure = parseInt(document.getElementById('tenure').value);

      const res = await fetch('/api/v1/emi/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          loan_amount: amount,
          annual_interest_rate: rate,
          tenure_months: tenure
        })
      });

      if (!res.ok) {
        alert("Failed to calculate EMI. Please check inputs.");
        return;
      }

      const data = await res.json();
      document.getElementById('val-emi').innerText = data.monthly_emi.toLocaleString(undefined, { minimumFractionDigits: 2 });
      document.getElementById('val-interest').innerText = data.total_interest.toLocaleString(undefined, { minimumFractionDigits: 2 });
      document.getElementById('val-total').innerText = data.total_payment.toLocaleString(undefined, { minimumFractionDigits: 2 });
      document.getElementById('result-box').style.display = 'block';
    }
  </script>
</body>
</html>
"""
