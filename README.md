# Wholesale Credit Risk & PD Analytics Engine

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://wholesale-credit-risk-engine.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An institutional-grade, end-to-end quantitative credit risk management pipeline and interactive simulation engine built entirely in Python using `pandas`, `numpy`, and `streamlit`.

This engine simulates a portfolio of **1,000 corporate clients**, assesses their fundamental credit risk profiles using a structured scorecard methodology, maps metrics to explicit **Probability of Default (PD)** benchmarks, and features a forward-looking **Macroeconomic Stress-Testing Module** aligned with modern banking regulatory concepts (Basel III/IV, EBA Adverse Scenario, and Fed CCAR frameworks).

---

## 🚀 Key Framework Features

* **Synthetic Corporate Portfolio Generator:** Models realistic balance sheets and income statement characteristics across 6 distinct sectors using customised log-normal and beta distributions.
* **Credit Scorecard Pipeline:** Implements a rule-based algorithm that vectorises the processing of core liquidity, leverage, and solvency metrics, assigning uniform risk grades ranging from `AAA-AA` (Investment Grade) down to `D` (Default). Includes a hard runtime guard against silent NaN propagation in PD fields.
* **Integrated Macro Shock Simulator:** Models economic stress across both the **income statement** (revenue contraction, EBITDA compression, net income deterioration) and **balance sheet** (sector-specific asset haircuts, cash burn, credit facility drawdowns inflating current liabilities) — calibrated against EBA 2023 Adverse Scenario guidelines with sector-specific GDP elasticity factors.
* **Config-Driven Architecture:** All model parameters — scorecard weights, PD bins, sector sensitivities, asset haircuts, stress scenario defaults — are externalised in a single `config.py` file with documented regulatory provenance. No magic numbers in business logic.
* **Validated Test Suite:** 11 pytest tests covering engine correctness, portfolio-level behavioural assertions, stress scenario mechanics, edge cases (zero interest, zero shock idempotency), and numeric floor guardrails.
* **Interactive Risk Executive Dashboard:** A Streamlit UI with functional sidebar controls enabling risk managers to dynamically adjust macro parameters and visualise rating migrations in real time.

---

## 📊 Analytical Methodology

The engine evaluates credit risk across three core corporate risk categories:

### 1. Liquidity Risk
Calculated via the **Current Ratio**:
$$\text{Current Ratio} = \frac{\text{Current Assets}}{\text{Current Liabilities}}$$
*Measures a corporation's ability to cover short-term obligations.*

### 2. Leverage Risk
Calculated via **Debt-to-EBITDA**:
$$\text{Debt to EBITDA} = \frac{\text{Total Debt}}{\text{EBITDA}}$$
*Quantifies the company's total debt burden relative to its operational cash generation. Negative EBITDA is preserved (not masked) and maps directly to the maximum risk score.*

### 3. Debt Service Risk
Calculated via the **Interest Coverage Ratio (ICR)**:
$$\text{Interest Coverage Ratio} = \frac{\text{EBITDA}}{\text{Interest Expense}}$$
*Measures how easily a company can pay interest on its outstanding debt.*

### Score Assignment & Risk Migration
Ratios are assigned individual scores ($1 \text{ to } 5$) based on institutional thresholds, weighted (**40% Leverage, 40% Debt Service, 20% Liquidity**), and translated into a final Probability of Default (PD) and credit rating grade.

### Exposure-Weighted Portfolio PD
Portfolio PD is computed as an **exposure-weighted average** using total debt as the EAD (Exposure at Default) proxy, consistent with Basel III internal ratings-based (IRB) methodology:

$$\text{Portfolio PD} = \frac{\sum_{i} PD_i \times EAD_i}{\sum_{i} EAD_i}$$

*This ensures larger, more exposed borrowers contribute proportionally more to the portfolio risk metric — unlike a naïve arithmetic mean.*

---

## 🛠️ Project Architecture

```text
├── data/                           # Generated output artefacts (git-ignored)
│   ├── corporate_portfolio.csv     # Raw generated client financials
│   ├── portfolio_with_scores.csv   # Computed baseline scores & risk grades
│   └── portfolio_stressed.csv      # Post-recession portfolio metrics
├── src/
│   ├── config.py                   # Centralised model parameters & regulatory constants
│   ├── data_gen.py                 # Synthetic corporate client generator
│   ├── pd_engine.py                # Ratio engine, scorecard mapping, NaN guardrails
│   └── stress_test.py              # Integrated macro shock simulation (IS + BS)
├── tests/
│   ├── conftest.py                 # Pytest fixtures (healthy firm, distressed firm, portfolio)
│   └── test_risk_engine.py         # 11-test validation suite
├── main.py                         # Production backend pipeline runner
├── app.py                          # Streamlit interactive web application
└── requirements.txt                # Project dependencies
```

---

## ⚙️ Stress Testing Design

The macro shock module applies an **integrated two-statement shock** across both Income Statement and Balance Sheet, parameterised through `config.py`:

| Shock Component | Mechanism | Config Parameter |
|---|---|---|
| Revenue / EBITDA contraction | GDP shock × sector elasticity | `DEFAULT_GDP_SHOCK`, `SECTOR_SENSITIVITIES` |
| Net income deterioration | 1.3× operating leverage amplifier | Hardcoded multiplier, intentional |
| Asset value compression | Sector-specific haircut applied to `total_assets` | `SECTOR_ASSET_HAIRCUTS` |
| Cash burn | 1.5× severity factor on `cash` | Inline constant |
| Credit facility drawdowns | `current_liabilities` *increase* under stress | Inline constant |
| Interest expense spike | Rate hike (bps) × total debt stock | `DEFAULT_RATE_HIKE_BPS` |

**Sector GDP Elasticities** (sourced from EBA Adverse Scenario calibration):

| Sector | Elasticity Factor |
|---|---|
| Real Estate | 1.5× |
| Retail | 1.3× |
| Manufacturing | 1.1× |
| Energy | 1.0× |
| Technology | 0.6× |
| Healthcare | 0.4× |

---

## 🧪 Test Suite

Run the full validation suite from the project root:

```bash
pytest tests/ -v
```

**11 tests across two modules:**

| Test | What It Validates |
|---|---|
| `test_negative_ebitda_yields_highest_risk_score` | Negative EBITDA maps to `lev_score=1`, not masked |
| `test_no_nan_pd_for_healthy_firm` | No NaN leakage in PD pipeline |
| `test_healthy_firm_scores_better_than_distressed` | PD ordering is monotonically correct |
| `test_score_weights_sum_to_one` | Config integrity: weights must equal 1.0 |
| `test_pipeline_handles_zero_interest_expense` | Zero ICR denominator doesn't produce inf/NaN |
| `test_stress_reduces_ebitda` | Stressed EBITDA < baseline EBITDA |
| `test_stress_increases_current_liabilities` | Credit lines called under stress |
| `test_stress_increases_interest_expense` | Rate hike propagates to interest expense |
| `test_stress_produces_more_defaults` | Severe stress → more `D`-grade firms |
| `test_zero_shock_leaves_portfolio_unchanged` | Zero shock = idempotent operation |
| `test_no_negative_values_after_shock` | Numeric floor prevents impossible negatives |

---

## 💻 Technical Setup & Installation

### Prerequisites

Tested on Linux distributions (**Pop!_OS / Ubuntu**). Ensure Python 3.8+ is installed.

```bash
sudo apt update
sudo apt install python3-pip python3-venv -y
```

### 1. Environment Setup

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/wholesale-credit-risk-engine.git
cd wholesale-credit-risk-engine

python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Execution Options

**Option A — Run the Backend Pipeline:**

```bash
python main.py
```

Executes the full pipeline: data generation → credit scoring → stress testing → saves all outputs to `/data`.

**Option B — Launch the Interactive Dashboard:**

```bash
streamlit run app.py
```

Deploys locally to `http://localhost:8501`. Adjust macro sliders and observe rating migrations in real time.

**Option C — Run the Test Suite:**

```bash
pytest tests/ -v
```

---

## 📈 Sample Output (Baseline vs Stressed)

```
=============================================
    RATING MIGRATION (BASELINE vs STRESSED)
=============================================
            Baseline (Healthy)  Stressed (Recession)
risk_grade
AAA-AA               89                   74
A-BBB               185                   88
BB                  350                  255
B                   214                  290
CCC-C               132                  200
D                    30                   93
=============================================
Exposure-Weighted Avg Portfolio PD (Base):     4.43%
Exposure-Weighted Avg Portfolio PD (Stressed): 7.04%
```

Under a severe macro shock (15% GDP contraction, +300bps rate spike), the engine successfully flags leveraged, vulnerable corporates — defaults (`Risk Grade D`) more than **triple**, and exposure-weighted portfolio PD expands from **4.43% to 7.04%**, consistent with EBA Adverse Scenario migration patterns observed in 2022–2023 stress exercises.

---

## 📄 License

This project is open-source and available under the MIT License.