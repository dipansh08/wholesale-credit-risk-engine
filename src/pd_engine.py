import pandas as pd
import numpy as np

def calculate_ratios(df):
    """Calculates core credit risk financial ratios."""
    # Avoid division by zero by replacing 0 or negative values with small positive numbers where appropriate
    df['current_ratio'] = df['current_assets'] / df['current_liabilities'].replace(0, 0.01)
    df['debt_to_ebitda'] = df['total_debt'] / df['ebitda'].apply(lambda x: max(x, 1000))
    df['interest_coverage'] = df['ebitda'] / df['interest_expense'].replace(0, 0.01)
    return df

def score_metrics(df):
    """Scores financial ratios from 1 (highest risk) to 5 (lowest risk)."""

    # 1. Current Ratio Scoring (Liquidity)
    df['liq_score'] = pd.cut(df['current_ratio'],
                             bins=[-np.inf, 0.8, 1.2, 1.5, 2.0, np.inf],
                             labels=[1, 2, 3, 4, 5]).astype(int)

    # 2. Debt to EBITDA Scoring (Leverage) - Note: Lower debt/ebitda is BETTER, so bins are reversed
    df['lev_score'] = pd.cut(df['debt_to_ebitda'],
                             bins=[-np.inf, 1.5, 3.0, 4.5, 6.0, np.inf],
                             labels=[5, 4, 3, 2, 1]).astype(int)

    # 3. Interest Coverage Scoring (Solvency)
    df['solv_score'] = pd.cut(df['interest_coverage'],
                             bins=[-np.inf, 1.0, 2.0, 4.0, 6.0, np.inf],
                             labels=[1, 2, 3, 4, 5]).astype(int)
    return df

def map_score_to_pd_and_grade(df):
    """Computes a weighted credit score, maps it to a PD, and assigns a Credit Grade."""
    
    # Weights: Leverage (40%), Debt Service (40%), Liquidity (20%)
    df['total_credit_score'] = (df['lev_score'] * 0.40) + (df['solv_score'] * 0.40) + (df['liq_score'] * 0.20)
    
    # FIX: Floor adjusted to 0.0 and include_lowest=True ensures scores of 1.0 are safely captured.
    score_bins = [0.0, 1.8, 2.5, 3.2, 3.8, 4.3, 4.7, 5.1]
    
    # Standard Basel-style PD assignments
    pd_mapping = [0.250, 0.120, 0.060, 0.030, 0.015, 0.005, 0.0005] 
    
    df['pd'] = pd.cut(
        df['total_credit_score'], 
        bins=score_bins, 
        labels=pd_mapping, 
        include_lowest=True
    ).astype(float)
    
    # PRODUCTION GUARDRAIL: Explicitly check for data leakage before assigning grades
    if df['pd'].isna().any():
        missing_count = df['pd'].isna().sum()
        raise ValueError(f"CRITICAL RISK ENGINE ERROR: {missing_count} clients generated NaN PDs due to bin misalignment.")
    
    # Map PD to institutional Credit Risk Rating Grades
    grade_bins = [-1, 0.0009, 0.01, 0.04, 0.08, 0.15, np.inf]
    grade_labels = ['AAA-AA', 'A-BBB', 'BB', 'B', 'CCC-C', 'D']
    df['risk_grade'] = pd.cut(df['pd'], bins=grade_bins, labels=grade_labels)
    
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