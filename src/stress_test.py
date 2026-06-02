import pandas as pd
import numpy as np
import config as cfg # Import configuration rules
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade

def apply_macro_shocks(df, gdp_shock_pct=cfg.DEFAULT_GDP_SHOCK, rate_hike_bps=cfg.DEFAULT_RATE_HIKE_BPS):
    """
    Applies an integrated macroeconomic shock to both the Income Statement 
    and Balance Sheet metrics based on sector-specific elasticities from config.
    """
    stressed_df = df.copy()
    
    # Iterate using config-driven sensibilities
    for sector, multiplier in cfg.SECTOR_SENSITIVITIES.items():
        sector_mask = stressed_df['sector'] == sector
        severity_factor = gdp_shock_pct * multiplier
        revenue_impact = 1.0 - severity_factor
        
        # Income statement shocks
        stressed_df.loc[sector_mask, 'revenue'] *= revenue_impact
        stressed_df.loc[sector_mask, 'ebitda'] *= revenue_impact
        stressed_df.loc[sector_mask, 'net_income'] *= (1.0 - (severity_factor * 1.3))
        
        # Balance sheet shocks
        asset_drop_multiplier = 0.8 if sector == 'Real Estate' else 0.95
        stressed_df.loc[sector_mask, 'total_assets'] *= (1.0 - (severity_factor * asset_drop_multiplier))
        stressed_df.loc[sector_mask, 'cash'] *= (1.0 - (severity_factor * 1.5))
        stressed_df.loc[sector_mask, 'current_assets'] *= (1.0 - (severity_factor * 0.5))
        stressed_df.loc[sector_mask, 'current_liabilities'] *= (1.0 + (severity_factor * 0.8))
        
    # Interest rate tightening
    rate_increase = rate_hike_bps / 10000
    additional_interest = stressed_df['total_debt'] * rate_increase
    stressed_df['interest_expense'] += additional_interest
    
    numeric_cols = stressed_df.select_dtypes(include=[np.number]).columns
    stressed_df[numeric_cols] = stressed_df[numeric_cols].clip(lower=0)
    
    return stressed_df

def run_stress_test_pipeline(input_path='data/portfolio_with_scores.csv', output_path='data/portfolio_stressed.csv'):
    """Loads baseline portfolio, applies shocks, and recalculates risk grades."""
    print("Loading baseline portfolio data...")
    baseline_df = pd.read_csv(input_path)

    print("\nTriggering Economic Recession Scenario...")
    print(" -> Simulating severe GDP contraction across sectors...")
    print(" -> Injecting +300bps Interest Rate Spike on corporate debt...")

    # Apply Shocks
    stressed_df = apply_macro_shocks(baseline_df, gdp_shock_pct=0.15, rate_hike_bps=300)

    # Re-run through the scoring engine mechanics
    stressed_df = calculate_ratios(stressed_df)
    stressed_df = score_metrics(stressed_df)
    stressed_df = map_score_to_pd_and_grade(stressed_df)

    # Save stressed results
    stressed_df.to_csv(output_path, index=False)
    print(f"\nStress testing completed! Stressed portfolio saved to '{output_path}'.")

    # Generate Comparison View
    print("\n=============================================")
    print("    RATING MIGRATION (BASELINE vs STRESSED)  ")
    print("=============================================")

    base_counts = baseline_df['risk_grade'].value_counts().sort_index()
    stress_counts = stressed_df['risk_grade'].value_counts().sort_index()

    comparison_df = pd.DataFrame({
        'Baseline (Healthy)': base_counts,
        'Stressed (Recession)': stress_counts
    }).fillna(0).astype(int)

    print(comparison_df)
    print("=============================================")

    # FIX: Calculate true Exposure-Weighted Average Portfolio PD using total_debt as EAD
    avg_pd_base = np.average(baseline_df['pd'], weights=baseline_df['total_debt']) * 100
    avg_pd_stress = np.average(stressed_df['pd'], weights=stressed_df['total_debt']) * 100
    
    print(f"Exposure-Weighted Avg Portfolio PD (Base):    {avg_pd_base:.2f}%")
    print(f"Exposure-Weighted Avg Portfolio PD (Stressed):{avg_pd_stress:.2f}%")

if __name__ == "__main__":
    run_stress_test_pipeline()