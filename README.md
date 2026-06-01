# Wholesale Credit Risk & PD Analytics Engine

An institutional-grade, end-to-end quantitative credit risk management pipeline and interactive simulation engine built entirely in Python using `pandas`, `numpy`, and `streamlit`. 

This engine simulates a portfolio of **1,000 corporate clients**, assesses their fundamental credit risk profiles using a structured scorecard methodology, maps metrics to explicit **Probability of Default (PD)** benchmarks, and features a forward-looking **Macroeconomic Stress-Testing Module** aligned with modern banking regulatory concepts (Basel III/IV framework framework frameworks).

---

## 🚀 Key Framework Features

* **Synthetic Corporate Portfolio Generator:** Models realistic balance sheets and income statement characteristics across 6 distinct sectors using customized log-normal and beta distributions.
* **Credit Scorecard Pipeline:** Implements a rule-based algorithm that vectorizes the processing of core liquidity, leverage, and solvency metrics, assigning uniform risk grades ranging from `AAA-AA` (Investment Grade) down to `D` (Default).
* **Macroeconomic Shock Simulator:** Models economic stress by assessing revenue contraction and monetary policy adjustments (+300bps interest rate shocks) factoring in unique sector elasticities.
* **Interactive Risk Executive Dashboard:** Includes a user interface with functional sidebar controls enabling risk managers to dynamically slide macro metrics and visualize rating migrations instantly.

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
*Quantifies the company's total debt burden relative to its operational cash generation.*

### 3. Debt Service Risk
Calculated via the **Interest Coverage Ratio (ICR)**:
$$\text{Interest Coverage Ratio} = \frac{\text{EBITDA}}{\text{Interest Expense}}$$
*Measures how easily a company can pay interest on its outstanding debt.*

### Score Assignment & Risk Migration
Ratios are assigned individual scores ($1 \text{ to } 5$) based on custom institutional thresholds, weighted (**40% Leverage, 40% Debt Service, 20% Liquidity**), and translated into a final Probability of Default (PD) and credit rating grade.

---

## 🛠️ Project Architecture

The workspace is split into decoupled, modular components following strict software engineering principles:

```text
├── data/
│   ├── corporate_portfolio.csv     # Raw generated client financials
│   ├── portfolio_with_scores.csv   # Computed baseline scores & risk grades
│   └── portfolio_stressed.csv      # Post-recession portfolio metrics
├── src/
│   ├── data_gen.py                 # Core synthetic client generator
│   ├── pd_engine.py                # Ratio engine and credit scorecard mapping
│   └── stress_test.py              # Macro shock simulation and sector elasticity logic
├── main.py                         # Production backend automation runner
├── app.py                          # Streamlit interactive web application UI
├── requirements.txt                # Project code library dependencies
└── README.md                       # Documentation