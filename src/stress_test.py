import pandas as pd
import numpy as np
# Import functions from your existing PD engine to re-score the stressed data
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade

def apply_macro_shocks(df, gdp_shock_pct=0.15, rate_hike_bps=300):
    """
    Applies macroeconomic shocks to the corporate financials.
    - gdp_shock_pct: Overall revenue reduction factor (e.g., 0.15 = 15% drop)
    - rate_hike_bps: Basis point increase to borrowing costs (e.g., 300 = +3.0%)
    """
    stressed_df = df.copy()

    # 1. Sector-specific revenue & EBITDA elasticities (Some sectors are more cyclical)
    sector_sensitivities = {
        'Real Estate': 1.5,
        'Retail': 1.3,
        'Manufacturing': 1.1,
        'Energy': 1.0,
        'Technology': 0.6,
        'Healthcare': 0.4
    }

    # Apply revenue and EBITDA shocks based on sector vulnerability
    for sector, multiplier in sector_sensitivities.items():
        sector_mask = stressed_df['sector'] == sector
        impact_factor = 1.0 - (gdp_shock_pct * multiplier)

        # Shock Revenue and EBITDA
        stressed_df.loc[sector_mask, 'revenue'] *= impact_factor
        stressed_df.loc[sector_mask, 'ebitda'] *= impact_factor
        stressed_df.loc[sector_mask, 'net_income'] *= (impact_factor * 0.8) # Net income drops faster due to fixed costs

    # 2. Interest Rate Shock
    # Convert bps to decimal (300 bps = 0.03)
    rate_increase = rate_hike_bps / 10000

    # Calculate additional interest expense on existing total debt
    additional_interest = stressed_df['total_debt'] * rate_increase
    stressed_df['interest_expense'] += additional_interest

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