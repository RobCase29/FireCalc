import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Union

# Set page configuration
st.set_page_config(
    page_title="Retirement Dashboard",
    page_icon="💰",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    :root {
        --background-color: #ffffff;
        --secondary-background-color: #f0f2f6;
        --text-color: #262730;
        --input-background-color: #ffffff;
    }
    body {
        font-family: 'Nunito', sans-serif;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .sidebar .sidebar-content {
        background-color: var(--secondary-background-color);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 12px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)


# Helper functions

def parse_currency(value: Union[str, int, float]) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        value = value.replace('$', '').replace(',', '')
        return float(value)
    except Exception:
        return None


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


# Deterministic Simulation Function
@st.cache_data

def calculate_deterministic_retirement(initial_capital: float, annual_expenses: float, years: int, return_rate: float, inflation_rate: float) -> Tuple[List[float], List[float], List[float]]:
    capital = [initial_capital]
    expenses = [annual_expenses]
    withdrawal_rates = [annual_expenses / initial_capital * 100]
    for year in range(1, years + 1):
        # Calculate expenses with inflation
        new_expense = expenses[-1] * (1 + inflation_rate/100)
        expenses.append(new_expense)
        # Portfolio growth
        growth = capital[-1] * (return_rate/100)
        new_capital = capital[-1] + growth - new_expense
        new_capital = max(new_capital, 0)
        capital.append(new_capital)
        prev_cap = capital[-2] if capital[-2] > 0 else 1
        withdrawal_rates.append(new_expense / prev_cap * 100)
        if new_capital <= 0:
            break
    return capital, expenses, withdrawal_rates


def plot_deterministic_simulation(capital: List[float], expenses: List[float]) -> None:
    years = list(range(len(capital)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=capital, mode='lines+markers', name='Capital'))
    fig.add_trace(go.Scatter(x=years, y=expenses, mode='lines+markers', name='Annual Expenses'))
    fig.update_layout(title="Deterministic Retirement Simulation",
                      xaxis_title="Years",
                      yaxis_title="Amount ($)",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)


# Monte Carlo Simulation Functions
risk_allocations = {
    "conservative": {"stocks": 0.4, "bonds": 0.5, "cash": 0.1},
    "moderate": {"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
    "aggressive": {"stocks": 0.8, "bonds": 0.15, "cash": 0.05},
}

asset_returns = {
    "stocks": {"mean": 0.10, "std": 0.15},
    "bonds": {"mean": 0.05, "std": 0.06},
    "cash": {"mean": 0.02, "std": 0.01},
}

def simulate_monthly_return(allocation: Dict[str, float]) -> float:
    monthly_ret = 0.0
    for asset, weight in allocation.items():
        mean = asset_returns[asset]["mean"] / 12
        std = asset_returns[asset]["std"] / np.sqrt(12)
        monthly_ret += weight * np.random.normal(mean, std)
    return monthly_ret


def run_portfolio_simulation(current_savings: float, monthly_savings: float, months: int, allocation: Dict[str, float]) -> List[float]:
    portfolio = [current_savings]
    for _ in range(months):
        ret = simulate_monthly_return(allocation)
        new_value = portfolio[-1] * (1 + ret) + monthly_savings
        portfolio.append(new_value)
    return portfolio


@st.cache_data

def run_monte_carlo_simulation(current_savings: float, monthly_savings: float, years: int, risk_profile: str, num_simulations: int) -> pd.DataFrame:
    months = years * 12
    allocation = risk_allocations[risk_profile]
    simulation_results = []
    for i in range(num_simulations):
        sim = run_portfolio_simulation(current_savings, monthly_savings, months, allocation)
        simulation_results.append(sim)
    # Convert to DataFrame; each row is a month, each column is a simulation
    df = pd.DataFrame(simulation_results).T
    return df


def plot_monte_carlo_simulation(df: pd.DataFrame) -> None:
    # Calculate percentile statistics per month
    median = df.median(axis=1)
    perc10 = df.quantile(0.1, axis=1)
    perc90 = df.quantile(0.9, axis=1)
    months = df.index

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=median, mode='lines', name='Median Portfolio'))
    fig.add_trace(go.Scatter(x=months, y=perc10, mode='lines', name='10th Percentile', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=months, y=perc90, mode='lines', name='90th Percentile', line=dict(dash='dash')))

    fig.update_layout(title="Monte Carlo Simulation of Portfolio Growth",
                      xaxis_title="Months",
                      yaxis_title="Portfolio Value ($)",
                      template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

    # Final portfolio distributions
    final_values = df.iloc[-1]
    fig_hist = px.histogram(final_values, nbins=30, title="Distribution of Final Portfolio Values")
    st.plotly_chart(fig_hist, use_container_width=True)


# Retirement Needs Calculation

def calculate_future_value(current_savings: float, monthly_savings: float, years: int, annual_return_rate: float) -> float:
    months = years * 12
    monthly_rate = (1 + annual_return_rate)**(1/12) - 1
    fv = current_savings
    for _ in range(months):
        fv = fv * (1 + monthly_rate) + monthly_savings
    return fv


def calculate_retirement_needs(current_age: int, retirement_age: int, current_savings: float, monthly_savings: float, annual_expenses: float, annual_return_rate: float, inflation_rate: float, life_expectancy: int) -> Dict[str, float]:
    years_to_retirement = retirement_age - current_age
    savings_at_retirement = calculate_future_value(current_savings, monthly_savings, years_to_retirement, annual_return_rate)
    adjusted_expenses = annual_expenses * ((1 + inflation_rate)**years_to_retirement)
    # Using a 4% safe withdrawal rate
    required_nest_egg = adjusted_expenses / 0.04
    return {
        "savings_at_retirement": savings_at_retirement,
        "required_nest_egg": required_nest_egg,
        "annual_expenses_at_retirement": adjusted_expenses
    }


# Main Dashboard
st.title("💰 Comprehensive Retirement Dashboard")
st.markdown("Explore various retirement planning tools, from deterministic simulations to Monte Carlo analyses and retirement needs calculations.")

# Sidebar for navigation
dashboard_mode = st.sidebar.radio("Select Dashboard Mode", ["Deterministic Simulation", "Monte Carlo Simulation", "Retirement Needs Calculation"])

if dashboard_mode == "Deterministic Simulation":
    st.header("Deterministic Retirement Simulation")
    # Input parameters
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        init_cap = st.text_input("Initial Capital", value=format_currency(1000000))
    with col2:
        ann_exp = st.text_input("Annual Expenses", value=format_currency(40000))
    with col3:
        years = st.slider("Years", 1, 100, 30)
    with col4:
        ret_rate = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0, step=0.1)
    with col5:
        infl_rate = st.slider("Expected Annual Inflation (%)", 0.0, 10.0, 3.0, step=0.1)
    
    # Parse inputs
    init_cap_val = parse_currency(init_cap) or 1000000
    ann_exp_val = parse_currency(ann_exp) or 40000
    
    # Run simulation
    capital, expenses, wd_rates = calculate_deterministic_retirement(init_cap_val, ann_exp_val, years, ret_rate, infl_rate)
    st.subheader("Simulation Results")
    st.write(f"Final Capital: {format_currency(capital[-1])}")
    st.write(f"Capital lasted for {len(capital)-1} years.")
    plot_deterministic_simulation(capital, expenses)
    
    # Display table of values
    sim_data = pd.DataFrame({
        "Year": list(range(len(capital))),
        "Capital": [format_currency(x) for x in capital],
        "Expenses": [format_currency(x) for x in expenses[:len(capital)]],
        "Withdrawal Rate (%)": [f"{x:.2f}" if not np.isnan(x) else "N/A" for x in wd_rates[:len(capital)]]
    })
    st.dataframe(sim_data)

elif dashboard_mode == "Monte Carlo Simulation":
    st.header("Monte Carlo Simulation for Portfolio Growth")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        current_savings = st.number_input("Current Savings ($)", value=1000000, step=10000)
    with col2:
        monthly_savings = st.number_input("Monthly Savings ($)", value=2000, step=100)
    with col3:
        years_sim = st.slider("Years to Simulate", 1, 100, 30)
    with col4:
        num_sim = st.number_input("Number of Simulations", value=500, step=50)
    
    risk_profile = st.selectbox("Risk Profile", ["conservative", "moderate", "aggressive"], index=1)
    
    df_sim = run_monte_carlo_simulation(current_savings, monthly_savings, years_sim, risk_profile, int(num_sim))
    st.subheader("Simulation Overview")
    plot_monte_carlo_simulation(df_sim)
    
elif dashboard_mode == "Retirement Needs Calculation":
    st.header("Retirement Needs Calculator")
    col1, col2, col3 = st.columns(3)
    with col1:
        current_age = st.number_input("Current Age", value=40, step=1)
    with col2:
        retirement_age = st.number_input("Retirement Age", value=65, step=1)
    with col3:
        life_expectancy = st.number_input("Life Expectancy", value=90, step=1)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        current_savings = st.number_input("Current Savings ($)", value=500000, step=10000)
    with col5:
        monthly_savings = st.number_input("Monthly Savings ($)", value=2000, step=100)
    with col6:
        annual_expenses = st.number_input("Current Annual Expenses ($)", value=40000, step=1000)
    
    col7, col8 = st.columns(2)
    with col7:
        ann_return = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0, step=0.1)
    with col8:
        infl_rate = st.slider("Expected Annual Inflation (%)", 0.0, 10.0, 3.0, step=0.1)
    
    results = calculate_retirement_needs(current_age, retirement_age, current_savings, monthly_savings, annual_expenses, ann_return/100, infl_rate/100, life_expectancy)
    
    st.subheader("Analysis")
    st.write(f"Estimated Savings at Retirement: {format_currency(results['savings_at_retirement'])}")
    st.write(f"Required Nest Egg (4% rule): {format_currency(results['required_nest_egg'])}")
    st.write(f"Projected Annual Expenses at Retirement: {format_currency(results['annual_expenses_at_retirement'])}")
    
    if results['savings_at_retirement'] >= results['required_nest_egg']:
        st.success("You're on track for a secure retirement!")
    else:
        st.error("You may need to increase savings or adjust your retirement plans.")

st.markdown("---")
st.markdown("**Note:** This dashboard provides estimates based on the inputs provided. Actual results may vary due to market fluctuations and other factors.") 