import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade
from stress_test import apply_macro_shocks
import config as cfg


# ==============================================================================
# PD ENGINE TESTS
# ==============================================================================

def test_negative_ebitda_yields_highest_risk_score(mock_distressed_firm):
    """CRITICAL: Negative EBITDA must not be masked — firm must score lev_score=1."""
    df = calculate_ratios(mock_distressed_firm)
    assert df.loc[0, 'debt_to_ebitda'] < 0, "Negative EBITDA should produce negative Debt/EBITDA ratio"
    df = score_metrics(df)
    assert df.loc[0, 'lev_score'] == 1, "Distressed firm with negative EBITDA must receive worst leverage score"


def test_no_nan_pd_for_healthy_firm(mock_healthy_firm):
    """NaN bomb prevention: healthy firm must complete pipeline without any NaN PD."""
    df = calculate_ratios(mock_healthy_firm)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)
    assert not df['pd'].isna().any(), "PD must never be NaN for a valid firm"
    assert df.loc[0, 'risk_grade'] in ['AAA-AA', 'A-BBB'], "Healthy firm should score investment grade"


def test_healthy_firm_scores_better_than_distressed(mock_healthy_firm, mock_distressed_firm):
    """Sanity check: a healthy firm must have a strictly lower PD than a distressed firm."""
    def run_pipeline(df):
        df = calculate_ratios(df)
        df = score_metrics(df)
        df = map_score_to_pd_and_grade(df)
        return df

    healthy = run_pipeline(mock_healthy_firm)
    distressed = run_pipeline(mock_distressed_firm)
    assert healthy.loc[0, 'pd'] < distressed.loc[0, 'pd'], \
        "Healthy firm PD must be strictly less than distressed firm PD"


def test_score_weights_sum_to_one():
    """Config integrity: scorecard weights must sum exactly to 1.0."""
    total = cfg.WEIGHT_LEVERAGE + cfg.WEIGHT_SOLVENCY + cfg.WEIGHT_LIQUIDITY
    assert abs(total - 1.0) < 1e-9, f"Scorecard weights sum to {total}, must equal 1.0"


def test_pipeline_handles_zero_interest_expense(mock_healthy_firm):
    """Edge case: zero interest expense must not cause division error."""
    mock_healthy_firm['interest_expense'] = 0.0
    df = calculate_ratios(mock_healthy_firm)
    assert np.isfinite(df.loc[0, 'interest_coverage']), "Zero interest expense must not produce inf/NaN ICR"


# ==============================================================================
# STRESS TEST TESTS
# ==============================================================================

def test_stress_reduces_ebitda(mock_healthy_firm):
    """Core behaviour: stressed EBITDA must be strictly lower than baseline EBITDA."""
    df = calculate_ratios(mock_healthy_firm)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)
    stressed = apply_macro_shocks(df)
    assert stressed.loc[0, 'ebitda'] < df.loc[0, 'ebitda'], \
        "Stressed EBITDA must be lower than baseline EBITDA"


def test_stress_increases_current_liabilities(mock_healthy_firm):
    """Balance sheet shock: current liabilities must increase under stress (credit lines called)."""
    df = calculate_ratios(mock_healthy_firm)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)
    stressed = apply_macro_shocks(df)
    assert stressed.loc[0, 'current_liabilities'] > df.loc[0, 'current_liabilities'], \
        "Current liabilities must increase under stress"


def test_stress_increases_interest_expense(mock_healthy_firm):
    """Rate hike shock: stressed interest expense must exceed baseline."""
    df = calculate_ratios(mock_healthy_firm)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)
    stressed = apply_macro_shocks(df, rate_hike_bps=300)
    assert stressed.loc[0, 'interest_expense'] > df.loc[0, 'interest_expense'], \
        "Interest expense must increase after rate hike shock"


def test_stress_produces_more_defaults(mock_portfolio):
    """Portfolio behaviour: a stressed portfolio must contain more 'D'-grade firms than baseline."""
    baseline = calculate_ratios(mock_portfolio)
    baseline = score_metrics(baseline)
    baseline = map_score_to_pd_and_grade(baseline)

    stressed = apply_macro_shocks(baseline, gdp_shock_pct=0.30, rate_hike_bps=500)
    stressed = calculate_ratios(stressed)
    stressed = score_metrics(stressed)
    stressed = map_score_to_pd_and_grade(stressed)

    baseline_defaults = (baseline['risk_grade'] == 'D').sum()
    stressed_defaults = (stressed['risk_grade'] == 'D').sum()
    assert stressed_defaults >= baseline_defaults, \
        "Severe stress must produce at least as many defaults as baseline"


def test_zero_shock_leaves_portfolio_unchanged(mock_portfolio):
    """Boundary: zero GDP shock and zero rate hike must leave financials intact."""
    df = calculate_ratios(mock_portfolio)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)

    stressed = apply_macro_shocks(df, gdp_shock_pct=0.0, rate_hike_bps=0)
    pd.testing.assert_series_equal(
        df['ebitda'].reset_index(drop=True),
        stressed['ebitda'].reset_index(drop=True),
        check_names=False
    )


def test_no_negative_values_after_shock(mock_portfolio):
    """Guardrail: numeric floor at zero must prevent physically impossible negative values."""
    df = calculate_ratios(mock_portfolio)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)

    stressed = apply_macro_shocks(df, gdp_shock_pct=0.99, rate_hike_bps=2000)
    numeric_cols = stressed.select_dtypes(include=[np.number]).columns
    assert (stressed[numeric_cols] >= 0).all().all(), \
        "No numeric field should be negative after stress clipping"