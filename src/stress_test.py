import pandas as pd
import numpy as np
import config as cfg
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade


def apply_macro_shocks(df, gdp_shock_pct=cfg.DEFAULT_GDP_SHOCK, rate_hike_bps=cfg.DEFAULT_RATE_HIKE_BPS):
    """
    Applies an integrated macroeconomic shock to both the Income Statement
    and Balance Sheet metrics based on sector-specific elasticities from config.

    Args:
        df: Baseline corporate portfolio DataFrame.
        gdp_shock_pct: Revenue/EBITDA contraction factor (e.g. 0.15 = 15% drop).
        rate_hike_bps: Basis point increase to borrowing costs (e.g. 300 = +3.0%).

    Returns:
        stressed_df: DataFrame with shocked financials, ready for re-scoring.
    """
    stressed_df = df.copy()

    for sector, multiplier in cfg.SECTOR_SENSITIVITIES.items():
        sector_mask = stressed_df['sector'] == sector
        severity_factor = gdp_shock_pct * multiplier
        revenue_impact = 1.0 - severity_factor

        # --- Income Statement Shocks ---
        stressed_df.loc[sector_mask, 'revenue'] *= revenue_impact
        stressed_df.loc[sector_mask, 'ebitda'] *= revenue_impact
        # Net income falls faster than EBITDA due to fixed cost operating leverage
        stressed_df.loc[sector_mask, 'net_income'] *= (1.0 - (severity_factor * 1.3))

        # --- Balance Sheet Shocks ---
        # Asset haircut sourced from config: Real Estate takes 0.80, all others 0.95
        asset_haircut = cfg.SECTOR_ASSET_HAIRCUTS.get(sector, 0.95)
        stressed_df.loc[sector_mask, 'total_assets'] *= (1.0 - (severity_factor * asset_haircut))

        # Cash burns faster than other current assets (liquidity drain)
        stressed_df.loc[sector_mask, 'cash'] *= (1.0 - (severity_factor * 1.5))
        stressed_df.loc[sector_mask, 'current_assets'] *= (1.0 - (severity_factor * 0.5))

        # Current liabilities INCREASE under stress as credit facilities get called
        stressed_df.loc[sector_mask, 'current_liabilities'] *= (1.0 + (severity_factor * 0.8))

    # --- Interest Rate Tightening ---
    # Convert basis points to decimal and apply to existing total debt stock
    rate_increase = rate_hike_bps / 10000
    stressed_df['interest_expense'] += stressed_df['total_debt'] * rate_increase

    # Floor all numeric columns at zero to prevent physically impossible negatives
    numeric_cols = stressed_df.select_dtypes(include=[np.number]).columns
    stressed_df[numeric_cols] = stressed_df[numeric_cols].clip(lower=0)

    return stressed_df


def run_stress_test_pipeline(
    input_path='data/portfolio_with_scores.csv',
    output_path='data/portfolio_stressed.csv',
    gdp_shock_pct=cfg.DEFAULT_GDP_SHOCK,        # FIX: use config constants, no more hardcoded values
    rate_hike_bps=cfg.DEFAULT_RATE_HIKE_BPS
):
    """Loads baseline portfolio, applies shocks, and recalculates risk grades."""
    print("Loading baseline portfolio data...")
    baseline_df = pd.read_csv(input_path)

    print(f"\nTriggering Economic Recession Scenario (GDP shock: {gdp_shock_pct*100:.0f}%, "
          f"Rate hike: {rate_hike_bps}bps)...")
    print(" -> Simulating severe GDP contraction across sectors...")
    print(" -> Injecting interest rate spike on corporate debt stock...")
    print(" -> Applying balance sheet and liquidity compression...")

    stressed_df = apply_macro_shocks(baseline_df, gdp_shock_pct=gdp_shock_pct, rate_hike_bps=rate_hike_bps)
    stressed_df = calculate_ratios(stressed_df)
    stressed_df = score_metrics(stressed_df)
    stressed_df = map_score_to_pd_and_grade(stressed_df)

    stressed_df.to_csv(output_path, index=False)
    print(f"\nStress testing completed! Stressed portfolio saved to '{output_path}'.")

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

    # Exposure-Weighted Average PD using total_debt as EAD proxy
    avg_pd_base = np.average(baseline_df['pd'], weights=baseline_df['total_debt']) * 100
    avg_pd_stress = np.average(stressed_df['pd'], weights=stressed_df['total_debt']) * 100

    print(f"Exposure-Weighted Avg Portfolio PD (Base):     {avg_pd_base:.2f}%")
    print(f"Exposure-Weighted Avg Portfolio PD (Stressed): {avg_pd_stress:.2f}%")


if __name__ == "__main__":
    run_stress_test_pipeline()