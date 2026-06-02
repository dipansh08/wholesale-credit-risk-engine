import pytest
import pandas as pd

@pytest.fixture
def mock_healthy_firm():
    return pd.DataFrame({
        'client_id': ['CORP-0001'],
        'sector': ['Technology'],
        'total_assets': [10_000_000.0],
        'current_assets': [5_000_000.0],
        'cash': [2_000_000.0],
        'total_debt': [2_000_000.0],
        'current_liabilities': [2_500_000.0],
        'revenue': [8_000_000.0],
        'ebitda': [2_000_000.0],
        'net_income': [1_000_000.0],
        'interest_expense': [120_000.0]
    })

@pytest.fixture
def mock_distressed_firm():
    # Genuinely toxic firm with negative EBITDA
    return pd.DataFrame({
        'client_id': ['CORP-9999'],
        'sector': ['Retail'],
        'total_assets': [10_000_000.0],
        'current_assets': [1_000_000.0],
        'cash': [50_000.0],
        'total_debt': [9_000_000.0],
        'current_liabilities': [8_000_000.0],
        'revenue': [3_000_000.0],
        'ebitda': [-5_000_000.0], # Negative EBITDA
        'net_income': [-6_000_000.0],
        'interest_expense': [800_000.0]
    })