"""
Institutional Credit Risk Engine - Configuration Parameters
Aligns with EBA / Fed CCAR Adverse Stress Testing Guidelines for Corporate Portfolios.
"""
import numpy as np

# ==============================================================================
# 1. DATA GENERATION ASSUMPTIONS (src/data_gen.py)
# ==============================================================================
PORTFOLIO_SIZE = 1000
RANDOM_SEED = 42

# Industry concentration weights (Must sum to 1.0)
SECTOR_DISTRIBUTION = {
    'Technology': 0.20,
    'Retail': 0.15,
    'Manufacturing': 0.25,
    'Energy': 0.10,
    'Healthcare': 0.15,
    'Real Estate': 0.15
}

# Baseline corporate borrowing rate assumptions (Mean: 6%, StdDev: 1.5%, bounded between 3% and 12%)
BASE_INTEREST_MEAN = 0.06
BASE_INTEREST_STD = 0.015
MIN_INTEREST_RATE = 0.03
MAX_INTEREST_RATE = 0.12

# ==============================================================================
# 2. SCORECARD WEIGHTS & BOUNDARIES (src/pd_engine.py)
# ==============================================================================
# Scorecard risk allocation parameters (Total must equal 1.0)
WEIGHT_LEVERAGE = 0.40
WEIGHT_SOLVENCY = 0.40
WEIGHT_LIQUIDITY = 0.20

# PD Score Assignment Threshold Bins
SCORE_BINS = [0.0, 1.8, 2.5, 3.2, 3.8, 4.3, 4.7, 5.1]
PD_MAPPING = [0.250, 0.120, 0.060, 0.030, 0.015, 0.005, 0.0005]

# Credit Rating Grade Mapping Cutoffs
GRADE_BINS = [-1, 0.0009, 0.01, 0.04, 0.08, 0.15, np.inf]
GRADE_LABELS = ['AAA-AA', 'A-BBB', 'BB', 'B', 'CCC-C', 'D']

# ==============================================================================
# 3. REGULATORY STRESS TESTING CONFIG (src/stress_test.py)
# ==============================================================================
# Default parameters calibrated against EBA Severe Adverse Scenario Frameworks
DEFAULT_GDP_SHOCK = 0.15      # 15% baseline revenue/EBITDA contraction across mid-market corporate books
DEFAULT_RATE_HIKE_BPS = 300   # +300bps monetary tightening interest rate spike

# Sector-specific economic sensitivities (GDP elasticity factors)
SECTOR_SENSITIVITIES = {
    'Real Estate': 1.5,
    'Retail': 1.3,
    'Manufacturing': 1.1,
    'Energy': 1.0,
    'Technology': 0.6,
    'Healthcare': 0.4
}

# Sector-specific asset haircut multipliers under stress.
# Applied as: total_assets *= (1 - severity_factor * haircut)
# Real Estate takes a heavier collateral hit (0.80) vs other sectors (0.95)
# Source: EBA 2023 Adverse Scenario asset valuation guidance.
SECTOR_ASSET_HAIRCUTS = {
    'Real Estate': 0.80,
    'Retail': 0.95,
    'Manufacturing': 0.95,
    'Energy': 0.95,
    'Technology': 0.95,
    'Healthcare': 0.95
}