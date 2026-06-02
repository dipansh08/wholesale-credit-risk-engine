import pytest
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade

def test_negative_ebitda_vulnerability(mock_distressed_firm):
    """CRITICAL TEST: Verifies that negative EBITDA is not masked and correctly yields highest risk score."""
    df_ratios = calculate_ratios(mock_distressed_firm)
    
    # Assert that Debt/EBITDA becomes negative, capturing operational bleed
    assert df_ratios.loc[0, 'debt_to_ebitda'] < 0
    
    df_scored = score_metrics(df_ratios)
    # Level score 1 means highest risk grade (CCC or D)
    assert df_scored.loc[0, 'lev_score'] == 1

def test_pipeline_nan_bomb_prevention(mock_healthy_firm):
    """Ensures no data boundary gaps leak NaN values into the PD calculations."""
    df_pipeline = calculate_ratios(mock_healthy_firm)
    df_pipeline = score_metrics(df_pipeline)
    df_pipeline = map_score_to_pd_and_grade(df_pipeline)
    
    assert not df_pipeline['pd'].isna().any()
    assert df_pipeline.loc[0, 'risk_grade'] in ['AAA-AA', 'A-BBB']