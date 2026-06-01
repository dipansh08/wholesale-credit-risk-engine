import pandas as pd
import numpy as np
import os

def generate_corporate_portfolio(n_clients=1000, seed=42):
    """
    Generates a realistic synthetic dataset of corporate clients with financial metrics.
    """
    np.random.seed(seed)
    
    # 1. Basic Company Info
    client_ids = [f"CORP-{i:04d}" for i in range(1, n_clients + 1)]
    sectors = ['Technology', 'Retail', 'Manufacturing', 'Energy', 'Healthcare', 'Real Estate']
    client_sectors = np.random.choice(sectors, size=n_clients, p=[0.20, 0.15, 0.25, 0.10, 0.15, 0.15])
    
    # 2. Financial Scale (Log-normal distribution to mimic real-world business sizes)
    # Most companies are mid-sized, a few are massive conglomerates
    total_assets = np.random.lognormal(mean=17.5, sigma=1.0, size=n_clients) # In Millions/Thousands
    
    # 3. Derive Income Statement & Balance Sheet items using realistic business ratios
    ebitda_margin = np.random.normal(loc=0.15, scale=0.05, size=n_clients)
    ebitda_margin = np.clip(ebitda_margin, 0.02, 0.45) # Keep margins realistic (2% to 45%)
    
    # Assume Asset Turnover (Revenue / Assets) centers around 0.8
    asset_turnover = np.random.normal(loc=0.8, scale=0.2, size=n_clients)
    revenue = total_assets * np.clip(asset_turnover, 0.1, 2.0)
    ebitda = revenue * ebitda_margin
    
    # Net Income (EBITDA minus depreciation/tax/interest assumptions)
    net_income = ebitda * np.random.normal(loc=0.4, scale=0.1, size=n_clients)
    
    # Leverage (Debt-to-Assets ratio between 20% and 80%)
    debt_to_assets = np.random.beta(a=2, b=3, size=n_clients) * 0.9 
    total_debt = total_assets * debt_to_assets
    
    # Interest Expense (Assuming an average baseline borrowing rate of 5% to 8%)
    interest_rate = np.random.normal(loc=0.06, scale=0.015, size=n_clients)
    interest_rate = np.clip(interest_rate, 0.03, 0.12)
    interest_expense = total_debt * interest_rate
    
    # Liquidity (Current Assets and Liabilities)
    # Current assets are typically 30-60% of total assets
    current_assets = total_assets * np.random.uniform(0.3, 0.6, size=n_clients)
    # Current liabilities tied loosely to current assets (giving varying liquidity ratios)
    current_liabilities = current_assets / np.random.normal(loc=1.5, scale=0.4, size=n_clients)
    current_liabilities = np.clip(current_liabilities, current_assets * 0.3, current_assets * 2.0)
    
    # Cash portion of current assets
    cash = current_assets * np.random.uniform(0.1, 0.4, size=n_clients)

    # 4. Construct DataFrame
    df = pd.DataFrame({
        'client_id': client_ids,
        'sector': client_sectors,
        'total_assets': np.round(total_assets, 2),
        'current_assets': np.round(current_assets, 2),
        'cash': np.round(cash, 2),
        'total_debt': np.round(total_debt, 2),
        'current_liabilities': np.round(current_liabilities, 2),
        'revenue': np.round(revenue, 2),
        'ebitda': np.round(ebitda, 2),
        'net_income': np.round(net_income, 2),
        'interest_expense': np.round(interest_expense, 2)
    })
    
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("Generating corporate portfolio dataset...")
    portfolio_df = generate_corporate_portfolio()
    
    # Save to CSV
    output_path = 'data/corporate_portfolio.csv'
    portfolio_df.to_csv(output_path, index=False)
    print(f"Success! Dataset containing {len(portfolio_df)} corporate clients saved to '{output_path}'.")