import pandas as pd
import numpy as np
import config as cfg  # Import the new configuration layer

def calculate_ratios(df):
    """Calculates core credit risk financial ratios with strict boundary guardrails."""
    df['current_ratio'] = df['current_assets'] / df['current_liabilities'].replace(0, 0.01)
    df['debt_to_ebitda'] = df['total_debt'] / df['ebitda'].apply(lambda x: 0.01 if x == 0 else x)
    df['interest_coverage'] = df['ebitda'] / df['interest_expense'].replace(0, 0.01)
    return df

def score_metrics(df):
    """Scores financial ratios from 1 (highest risk) to 5 (lowest risk)."""
    df['liq_score'] = pd.cut(df['current_ratio'], 
                             bins=[-np.inf, 0.8, 1.2, 1.5, 2.0, np.inf], 
                             labels=[1, 2, 3, 4, 5]).astype(int)
    
    df['lev_score'] = pd.cut(df['debt_to_ebitda'], 
                             bins=[-np.inf, 0.0, 1.5, 3.0, 4.5, 6.0, np.inf], 
                             labels=[1, 5, 4, 3, 2, 1], ordered=False).astype(int)
    
    df['solv_score'] = pd.cut(df['interest_coverage'], 
                             bins=[-np.inf, 1.0, 2.0, 4.0, 6.0, np.inf], 
                             labels=[1, 2, 3, 4, 5]).astype(int)
    return df

def map_score_to_pd_and_grade(df):
    """Computes a weighted credit score, maps it to a PD, and assigns a Credit Grade using Config limits."""
    # Use config weights
    df['total_credit_score'] = (df['lev_score'] * cfg.WEIGHT_LEVERAGE) + \
                               (df['solv_score'] * cfg.WEIGHT_SOLVENCY) + \
                               (df['liq_score'] * cfg.WEIGHT_LIQUIDITY)
    
    # Use config bins and mappings
    df['pd'] = pd.cut(
        df['total_credit_score'], 
        bins=cfg.SCORE_BINS, 
        labels=cfg.PD_MAPPING, 
        include_lowest=True
    ).astype(float)
    
    if df['pd'].isna().any():
        missing_count = df['pd'].isna().sum()
        raise ValueError(f"CRITICAL RISK ENGINE ERROR: {missing_count} clients generated NaN PDs due to bin misalignment.")
    
    df['risk_grade'] = pd.cut(df['pd'], bins=cfg.GRADE_BINS, labels=cfg.GRADE_LABELS)
    return df

def run_pd_pipeline(input_path='data/corporate_portfolio.csv', output_path='data/portfolio_with_scores.csv'):
    """Executes the complete baseline PD engine pipeline."""
    print("Loading data into PD Analytics Engine...")
    df = pd.read_csv(input_path)

    # Run processing functions
    df = calculate_ratios(df)
    df = score_metrics(df)
    df = map_score_to_pd_and_grade(df)

    # Save the output
    df.to_csv(output_path, index=False)
    print(f"PD Pipeline executed successfully! Output saved to '{output_path}'.")

    # Print portfolio health baseline snapshot
    print("\n--- Baseline Portfolio Distribution Summary ---")
    print(df['risk_grade'].value_counts().sort_index())

    return df

if __name__ == "__main__":
    run_pd_pipeline()