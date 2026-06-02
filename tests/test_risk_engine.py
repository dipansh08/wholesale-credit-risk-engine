import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from pd_engine import calculate_ratios

def test_calculate_ratios():
    dummy_data = pd.DataFrame({
        'current_assets': [200.0],
        'current_liabilities': [100.0],
        'total_debt': [400.0],
        'ebitda': [100.0]
    })
    
    processed_df = calculate_ratios(dummy_data)
    
    assert processed_df.loc[0, 'current_ratio'] == 2.0
    assert processed_df.loc[0, 'debt_to_ebitda'] == 4.0