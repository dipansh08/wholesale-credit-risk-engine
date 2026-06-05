import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


@pytest.fixture
def mock_healthy_firm():
    """A well-capitalised, low-leverage corporate client. Should score investment grade."""
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
    """A genuinely toxic firm with negative EBITDA. Should score D/CCC regardless of inputs."""
    return pd.DataFrame({
        'client_id': ['CORP-9999'],
        'sector': ['Retail'],
        'total_assets': [10_000_000.0],
        'current_assets': [1_000_000.0],
        'cash': [50_000.0],
        'total_debt': [9_000_000.0],
        'current_liabilities': [8_000_000.0],
        'revenue': [3_000_000.0],
        'ebitda': [-5_000_000.0],
        'net_income': [-6_000_000.0],
        'interest_expense': [800_000.0]
    })


@pytest.fixture
def mock_portfolio():
    """
    A small but representative 10-firm portfolio spanning all 6 sectors
    with a range of credit quality from investment-grade to near-default.
    Used for portfolio-level behavioural tests.
    """
    np.random.seed(42)
    sectors = ['Technology', 'Retail', 'Manufacturing', 'Energy', 'Healthcare', 'Real Estate',
               'Technology', 'Retail', 'Manufacturing', 'Energy']

    return pd.DataFrame({
        'client_id': [f'CORP-{i:04d}' for i in range(1, 11)],
        'sector': sectors,
        'total_assets':        [10e6, 5e6, 8e6, 15e6, 12e6, 20e6, 3e6, 7e6, 6e6, 9e6],
        'current_assets':      [5e6,  1e6, 3e6, 6e6,  5e6,  4e6,  1e6, 2e6, 2e6, 3e6],
        'cash':                [2e6,  0.2e6, 1e6, 2e6, 2e6,  1e6,  0.3e6, 0.5e6, 0.8e6, 1e6],
        'total_debt':          [2e6,  4e6, 5e6, 7e6,  3e6,  14e6, 2.5e6, 5e6, 4e6, 6e6],
        'current_liabilities': [2.5e6, 3e6, 2e6, 4e6, 2e6,  5e6,  1.5e6, 3e6, 2e6, 3.5e6],
        'revenue':             [8e6,  3e6, 7e6, 12e6, 10e6, 6e6,  2e6,  4e6, 5e6, 7e6],
        'ebitda':              [2e6,  0.2e6, 1e6, 2e6, 2.5e6, 0.8e6, 0.3e6, 0.1e6, 0.8e6, 1e6],
        'net_income':          [1e6, -0.5e6, 0.4e6, 0.8e6, 1.2e6, -0.3e6, 0.1e6, -0.2e6, 0.3e6, 0.4e6],
        'interest_expense':    [120e3, 280e3, 350e3, 420e3, 180e3, 700e3, 175e3, 350e3, 280e3, 360e3]
    })