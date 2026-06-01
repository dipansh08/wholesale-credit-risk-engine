import os
import sys

# Ensure src/ directory is in the system path so Python can find our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from data_gen import generate_corporate_portfolio
from pd_engine import run_pd_pipeline
from stress_test import run_stress_test_pipeline

def main():
    print("======================================================================")
    print("      WHOLESALE CREDIT RISK & PD ANALYTICS ENGINE - EXECUTIVE RUN     ")
    print("======================================================================\n")

    # 1. Step 1: Data Generation
    print("[STEP 1/3] Launching Corporate Data Generator...")
    portfolio_df = generate_corporate_portfolio(n_clients=1000, seed=42)
    os.makedirs('data', exist_ok=True)
    portfolio_df.to_csv('data/corporate_portfolio.csv', index=False)
    print(" -> Completed. Synthetic profile for 1,000 corporate clients created.\n")

    # 2. Step 2: Baseline PD Analytics Engine
    print("[STEP 2/3] Processing Credit Scoring Engine (Baseline Scenario)...")
    run_pd_pipeline(
        input_path='data/corporate_portfolio.csv',
        output_path='data/portfolio_with_scores.csv'
    )
    print("\n")

    # 3. Step 3: Macroeconomic Stress-Testing Module
    print("[STEP 3/3] Running Macroeconomic Stress-Testing Engine...")
    run_stress_test_pipeline(
        input_path='data/portfolio_with_scores.csv',
        output_path='data/portfolio_stressed.csv'
    )

    print("\n======================================================================")
    print("  Pipeline execution complete! All institutional outputs saved to /data ")
    print("======================================================================")

if __name__ == "__main__":
    main()