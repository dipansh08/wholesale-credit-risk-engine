import streamlit as tf
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Ensure src/ is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from stress_test import apply_macro_shocks
from pd_engine import calculate_ratios, score_metrics, map_score_to_pd_and_grade

# Set page layout to wide mode
st.set_page_config(page_title="Wholesale Credit Risk Engine", layout="wide")

st.title("📊 Wholesale Credit Risk & PD Analytics Dashboard")
st.markdown("---")

# Load baseline data
@st.cache_data
def load_base_data():
    # If the file doesn't exist, run main.py functions first to generate it
    if not os.path.exists('data/portfolio_with_scores.csv'):
        from data_gen import generate_corporate_portfolio
        df = generate_corporate_portfolio()
        df = calculate_ratios(df)
        df = score_metrics(df)
        df = map_score_to_pd_and_grade(df)
    else:
        df = pd.read_csv('data/portfolio_with_scores.csv')
    return df

baseline_df = load_base_data()

# ==========================================
# SIDEBAR - CONTROLS FOR MACRO SHOCKS
# ==========================================
st.sidebar.header("🕹️ Macroeconomic Stress Controls")
st.sidebar.markdown("Adjust macro parameters to instantly stress-test the corporate credit portfolio.")

gdp_shock = st.sidebar.slider(
    "GDP Contraction (Revenue Drop %)", 
    min_value=0, max_value=30, value=15, step=1
)

rate_hike = st.sidebar.slider(
    "Interest Rate Hike (Basis Points)", 
    min_value=0, max_value=600, value=300, step=50
)

# Run the stress logic on-the-fly based on slider inputs
stressed_df = apply_macro_shocks(baseline_df, gdp_shock_pct=(gdp_shock/100), rate_hike_bps=rate_hike)
stressed_df = calculate_ratios(stressed_df)
stressed_df = score_metrics(stressed_df)
stressed_df = map_score_to_pd_and_grade(stressed_df)

# ==========================================
# MAIN PAGE - KPI CARDS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

avg_pd_base = baseline_df['pd'].mean() * 100
avg_pd_stress = stressed_df['pd'].mean() * 100
defaults_base = (baseline_df['risk_grade'] == 'D').sum()
defaults_stress = (stressed_df['risk_grade'] == 'D').sum()

with col1:
    st.metric("Baseline Avg Portfolio PD", f"{avg_pd_base:.2f}%")
with col2:
    st.metric("Stressed Avg Portfolio PD", f"{avg_pd_stress:.2f}%", delta=f"{avg_pd_stress - avg_pd_base:+.2f}%", delta_color="inverse")
with col3:
    st.metric("Baseline Corporate Defaults", f"{defaults_base} / 1000")
with col4:
    st.metric("Stressed Corporate Defaults", f"{defaults_stress} / 1000", delta=f"+{defaults_stress - defaults_base} companies", delta_color="inverse")

st.markdown("---")

# ==========================================
# VISUALIZATIONS
# ==========================================
left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("📈 Credit Risk Grade Migration")
    
    # Structure data for comparison chart
    order = ['AAA-AA', 'A-BBB', 'BB', 'B', 'CCC-C', 'D']
    b_counts = baseline_df['risk_grade'].value_counts().reindex(order).fillna(0)
    s_counts = stressed_df['risk_grade'].value_counts().reindex(order).fillna(0)
    
    plot_df = pd.DataFrame({
        'Risk Grade': order,
        'Baseline (Healthy)': b_counts.values,
        'Stressed (Recession)': s_counts.values
    }).set_index('Risk Grade')
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    plot_df.plot(kind='bar', color=['#2b5c8f', '#d95f02'], ax=ax, width=0.7)
    ax.set_ylabel("Number of Corporate Clients")
    ax.set_xticklabels(order, rotation=0)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)

with right_chart:
    st.subheader("🏢 Sector Vulnerability Matrix (Stressed Avg PD)")
    
    # Calculate average PD by sector under stress
    sector_pd = stressed_df.groupby('sector')['pd'].mean().sort_values(ascending=False) * 100
    
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(x=sector_pd.values, y=sector_pd.index, palette="Reds_r", ax=ax)
    ax.set_xlabel("Average Probability of Default (PD) %")
    ax.set_ylabel("Industry Sector")
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("---")

# ==========================================
# PORTFOLIO DATA EXPLORER
# ==========================================
st.subheader("🔍 Corporate Portfolio Data Explorer")
sector_filter = st.selectbox("Filter Explorer by Sector:", ["All"] + list(baseline_df['sector'].unique()))

display_df = stressed_df.copy()
if sector_filter != "All":
    display_df = display_df[display_df['sector'] == sector_filter]

cols_to_show = ['client_id', 'sector', 'current_ratio', 'debt_to_ebitda', 'interest_coverage', 'pd', 'risk_grade']
st.dataframe(
    display_df[cols_to_show].rename(columns={
        'current_ratio': 'Current Ratio',
        'debt_to_ebitda': 'Debt/EBITDA',
        'interest_coverage': 'Interest Coverage',
        'pd': 'Stressed PD',
        'risk_grade': 'Stressed Grade'
    }).style.format({'Stressed PD': '{:.2%}'}), 
    use_container_width=True
)