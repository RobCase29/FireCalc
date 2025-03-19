import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Union, Optional, Dict
import numpy as np
from dataclasses import dataclass

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Retirement Withdrawal Calculator",
    page_icon="💰"
)

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600&family=Quicksand:wght@400;600&display=swap');

    body {
        font-family: 'Nunito', sans-serif;
    }
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .sidebar .sidebar-content {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    .sidebar .sidebar-content .stTextInput, .sidebar .sidebar-content .stSlider {
        color: var(--text-color);
    }
    .sidebar .sidebar-content .stTextInput input, .sidebar .sidebar-content .stSlider .stSliderLabel {
        color: var(--text-color);
    }
    .sidebar .sidebar-content .stTextInput input {
        background-color: var(--input-background-color);
        border: 1px solid #4CAF50;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stAlert {
        border-radius: 12px;
    }
    .stMarkdown {
        font-size: 16px;
    }
    .stTextInput label, .stSlider label {
        font-family: 'Quicksand', sans-serif;
        font-weight: 600;
    }
    .stTextInput input, .stSlider .stSliderLabel {
        font-family: 'Nunito', sans-serif;
    }
    .stTextInput input {
        border-radius: 8px;
    }
    .stSlider .stSliderTrack .stSliderTrackValue {
        border-radius: 8px;
    }
    .stSlider .stSliderTrack .stSliderTrackValue .stSliderTrackValueLabel {
        font-family: 'Nunito', sans-serif;
    }
    .stTable {
        font-family: 'Nunito', sans-serif;
    }
    .stTable th, .stTable td {
        padding: 10px;
    }
    .stTable th {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    .stTable td {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    .stTable tr:nth-child(even) td {
        background-color: var(--secondary-background-color);
    }
    .stTable tr:nth-child(odd) td {
        background-color: var(--background-color);
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def parse_currency(value: Union[str, int, float]) -> Optional[float]:
    if isinstance(value, (int, float)):
        return value
    value = value.replace('$', '').replace(',', '')
    try:
        return float(value)
    except ValueError:
        return None

def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def calculate_retirement(initial_capital, annual_expenses, years, return_rate, inflation_rate):
    capital = [initial_capital]
    expenses = [annual_expenses]
    withdrawal_rates = [annual_expenses / initial_capital * 100]
    
    for year in range(1, years + 1):
        # Calculate current expenses with inflation
        current_expenses = expenses[-1] * (1 + inflation_rate / 100)
        
        # Total expenses are just the current expenses
        total_expenses = current_expenses
        expenses.append(total_expenses)
        
        # Calculate growth of the capital
        growth = capital[-1] * (return_rate / 100)
        
        # Calculate new capital after growth and expenses
        new_capital = capital[-1] + growth - total_expenses
        capital.append(max(0, new_capital))
        
        # Calculate withdrawal rate
        withdrawal_rates.append(total_expenses / capital[-2] * 100 if capital[-2] > 0 else float('inf'))
        
        # Break if capital is depleted
        if new_capital <= 0:
            break
    
    return capital, expenses, withdrawal_rates

def find_sustainable_value(years, annual_expenses, return_rate, inflation_rate, find_capital, initial_capital):
    if find_capital:
        # Find the required initial capital for the given period
        low, high = 0, initial_capital * 10
        while low < high:
            mid = (low + high) / 2
            capital, _, _ = calculate_retirement(mid, annual_expenses, years, return_rate, inflation_rate)
            if capital[-1] > 0:
                high = mid
            else:
                low = mid + 1
        return low
    else:
        # Find the maximum sustainable annual expenses for the given period
        low, high = 0, annual_expenses * 10
        while low < high:
            mid = (low + high) / 2
            capital, _, _ = calculate_retirement(initial_capital, mid, years, return_rate, inflation_rate)
            if capital[-1] > 0:
                low = mid + 1
            else:
                high = mid
        return high

# Summary section
st.title("💰 Retirement Withdrawal Calculator")
st.markdown("""
This calculator helps you estimate how long your retirement savings will last based on your initial capital, annual expenses, and other factors. Adjust the inputs to see how different scenarios affect your retirement plan.
""")

# Input section
st.sidebar.header("Input Parameters")

# Initial Capital Input
initial_capital_input = st.sidebar.text_input(
    'Initial Capital',
    value=format_currency(1000000),  # Default value formatted
    help="Enter the initial capital amount. You can use dollar signs and commas."
)
initial_capital = parse_currency(initial_capital_input)
if initial_capital is None:
    st.sidebar.error("Please enter a valid dollar amount for Initial Capital")
    initial_capital = 1000000
else:
    # Reformat the input to display it correctly
    initial_capital_input = format_currency(initial_capital)

# Annual Expenses Input
annual_expenses_input = st.sidebar.text_input(
    'Annual Expenses',
    value=format_currency(40000),  # Default value formatted
    help="Enter your annual expenses. You can use dollar signs and commas."
)
annual_expenses = parse_currency(annual_expenses_input)
if annual_expenses is None:
    st.sidebar.error("Please enter a valid dollar amount for Annual Expenses")
    annual_expenses = 40000
else:
    # Reformat the input to display it correctly
    annual_expenses_input = format_currency(annual_expenses)

return_rate = st.sidebar.slider('Expected Annual Return (%)', 0.0, 15.0, 10.0, 0.1, help="The expected annual return on your investments.")
inflation_rate = st.sidebar.slider('Expected Annual Inflation (%)', 0.0, 10.0, 3.8, 0.1, help="The expected annual inflation rate.")

# Number of Years Input
years = st.sidebar.slider('Number of Years to Simulate', 1, 100, 30, help="The number of years to simulate.")

# Calculation
capital_over_time, expenses_over_time, withdrawal_rates = calculate_retirement(initial_capital, annual_expenses, years, return_rate, inflation_rate)

# Results section
st.header("Results")

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(len(capital_over_time))), y=capital_over_time, mode='lines', name='Capital'))
fig.add_trace(go.Scatter(x=list(range(len(expenses_over_time))), y=expenses_over_time, mode='lines', name='Annual Expenses'))
fig.update_layout(title='Projected Capital, Expenses, and Withdrawals Over Time', xaxis_title='Years', yaxis_title='Amount ($)', height=500, plot_bgcolor='var(--background-color)', paper_bgcolor='var(--background-color)', font=dict(color='var(--text-color)'))
st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

# Table
intervals = list(range(0, years + 1))  # Create a list of years from 0 to the specified number of years
data = {
    'Year': intervals,
    'Remaining Capital': [f'${capital_over_time[year]:,.2f}' if year < len(capital_over_time) else 'N/A' for year in intervals],
    'Annual Expenses': [f'${expenses_over_time[year]:,.2f}' if year < len(expenses_over_time) else 'N/A' for year in intervals],
    'Withdrawal Rate': [f'{withdrawal_rates[year]:.2f}%' if year < len(withdrawal_rates) else 'N/A' for year in intervals]
}
df = pd.DataFrame(data)

# Convert DataFrame to HTML and display it using st.markdown
st.markdown(
    df.to_html(index=False, escape=False),
    unsafe_allow_html=True
)

# Initial withdrawal rate
initial_withdrawal_rate = annual_expenses / initial_capital * 100
st.info(f"💡 Initial withdrawal rate: {initial_withdrawal_rate:.2f}%")

# Analysis
years_until_depletion = len(capital_over_time) - 1
if years_until_depletion < years:
    st.warning(f'⚠️ Warning: Capital depleted after {years_until_depletion} years.')
    
    # Calculate required initial capital for the specified number of years
    required_capital = find_sustainable_value(years, annual_expenses, return_rate, inflation_rate, True, initial_capital)
    st.info(f'💡 Required initial capital for {years} years: ${required_capital:,.2f}')
    
    # Calculate maximum sustainable annual expenses for the specified number of years
    max_expenses = find_sustainable_value(years, annual_expenses, return_rate, inflation_rate, False, initial_capital)
    st.info(f'💡 Maximum sustainable initial annual expenses for {years} years: ${max_expenses:,.2f}')
else:
    st.success(f'✅ Capital lasts for the entire {years} year period.')
    
    # Calculate remaining capital after the specified number of years
    final_capital = capital_over_time[-1]
    st.info(f'💡 Remaining capital after {years} years: ${final_capital:,.2f}')
    
    # Calculate total withdrawals over the specified number of years
    total_withdrawals = sum(expenses_over_time)
    st.info(f'💡 Total withdrawals over {years} years: ${total_withdrawals:,.2f}')

# Perpetuity calculations
st.subheader('Perpetuity Calculations')

# Calculate the real rate of return (after inflation)
real_return_rate = return_rate - inflation_rate

# Calculate the sustainable withdrawal amount in perpetuity
sustainable_withdrawal = initial_capital * (real_return_rate / 100)

st.info(f"💡 Sustainable annual withdrawal in perpetuity: ${sustainable_withdrawal:,.2f}")

# Calculate the withdrawal rate as a percentage of initial capital
perpetuity_withdrawal_rate = (sustainable_withdrawal / initial_capital) * 100
st.info(f"💡 Sustainable withdrawal rate in perpetuity: {perpetuity_withdrawal_rate:.2f}%")

# Calculate required initial capital for perpetuity based on current annual expenses
required_capital_perpetuity = annual_expenses / (real_return_rate / 100)
st.info(f"💡 Required initial capital for perpetuity (based on current annual expenses): ${required_capital_perpetuity:,.2f}")

# Compare current withdrawal to sustainable withdrawal
current_withdrawal = annual_expenses
if current_withdrawal > sustainable_withdrawal:
    st.warning(
        f"⚠️ Current withdrawal (${current_withdrawal:,.2f}) exceeds the sustainable withdrawal in perpetuity (${sustainable_withdrawal:,.2f})."
    )
else:
    st.success(
        f"✅ Current withdrawal (${current_withdrawal:,.2f}) is within the sustainable withdrawal limit for perpetuity (${sustainable_withdrawal:,.2f})."
    )

# Footer
st.markdown("""
    ---
    **Note:** This calculator provides estimates based on the inputs provided. Actual results may vary based on market conditions and other factors.
""")

@dataclass
class RetirementInputs:
    current_age: int
    retirement_age: int
    life_expectancy: int = 90
    current_savings: float = 0
    monthly_savings: float = 0
    annual_return_rate: float = 0.07
    inflation_rate: float = 0.03
    annual_expenses: float = 0
    additional_income: float = 0
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    tax_rate: float = 0.25
    portfolio_allocation: Dict[str, float] = None

class ModernRetirementCalculator:
    def __init__(self, inputs: RetirementInputs):
        self.inputs = inputs
        self.portfolio_allocations = {
            "conservative": {"stocks": 0.4, "bonds": 0.5, "cash": 0.1},
            "moderate": {"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
            "aggressive": {"stocks": 0.8, "bonds": 0.15, "cash": 0.05}
        }
        
        # Historical return assumptions
        self.asset_returns = {
            "stocks": {"mean": 0.10, "std": 0.15},
            "bonds": {"mean": 0.05, "std": 0.06},
            "cash": {"mean": 0.02, "std": 0.01}
        }

    def run_monte_carlo_simulation(self, num_simulations: int = 1000) -> pd.DataFrame:
        """Run Monte Carlo simulation for retirement projections"""
        years = self.inputs.life_expectancy - self.inputs.current_age
        months = years * 12
        results = []

        for _ in range(num_simulations):
            portfolio = self.simulate_portfolio_growth(months)
            results.append(portfolio)

        return pd.DataFrame(results).T

    def simulate_portfolio_growth(self, months: int) -> List[float]:
        """Simulate monthly portfolio growth with realistic market conditions"""
        portfolio_value = [self.inputs.current_savings]
        allocation = self.portfolio_allocations[self.inputs.risk_tolerance]

        for _ in range(months):
            current_value = portfolio_value[-1]
            monthly_return = self.calculate_monthly_return(allocation)
            
            # Apply monthly return and add contributions
            new_value = current_value * (1 + monthly_return) + self.inputs.monthly_savings
            portfolio_value.append(new_value)

        return portfolio_value

    def calculate_monthly_return(self, allocation: Dict[str, float]) -> float:
        """Calculate monthly return based on portfolio allocation"""
        monthly_return = 0
        for asset, weight in allocation.items():
            mean = self.asset_returns[asset]["mean"] / 12
            std = self.asset_returns[asset]["std"] / np.sqrt(12)
            monthly_return += weight * np.random.normal(mean, std)
        return monthly_return

    def get_retirement_analysis(self) -> Dict:
        """Generate comprehensive retirement analysis"""
        simulations = self.run_monte_carlo_simulation()
        
        return {
            "success_probability": self.calculate_success_probability(simulations),
            "projected_outcomes": self.get_projection_percentiles(simulations),
            "withdrawal_strategy": self.analyze_withdrawal_strategy(simulations),
            "risk_analysis": self.analyze_risk_metrics(simulations)
        }

    def calculate_success_probability(self, simulations: pd.DataFrame) -> float:
        """Calculate probability of retirement success"""
        final_values = simulations.iloc[-1]
        required_amount = self.calculate_required_nest_egg()
        return (final_values >= required_amount).mean()

    def calculate_required_nest_egg(self) -> float:
        """Calculate required nest egg using dynamic SWR"""
        years_in_retirement = self.inputs.life_expectancy - self.inputs.retirement_age
        inflation_adjusted_expenses = self.inputs.annual_expenses * \
            (1 + self.inputs.inflation_rate) ** (self.inputs.retirement_age - self.inputs.current_age)
        # Using dynamic SWR based on retirement duration
        safe_withdrawal_rate = 0.04 if years_in_retirement <= 30 else 0.03
        return inflation_adjusted_expenses / safe_withdrawal_rate

class RetirementCalculator:
    def __init__(self):
        self.current_age = 0
        self.retirement_age = 0
        self.current_savings = 0
        self.monthly_savings = 0
        self.annual_return_rate = 0.07  # 7% default
        self.inflation_rate = 0.03      # 3% default
        self.annual_expenses = 0
        self.additional_income = 0      # Social Security, pension, etc.
        
    def calculate_future_value(self, years):
        """Calculate future value of current savings plus monthly contributions"""
        fv = self.current_savings
        monthly_return = (1 + self.annual_return_rate) ** (1/12) - 1
        
        for _ in range(years * 12):
            fv = fv * (1 + monthly_return) + self.monthly_savings
            
        return fv
    
    def calculate_retirement_needs(self):
        """Calculate how much money needed for retirement"""
        years_until_retirement = self.retirement_age - self.current_age
        retirement_savings = self.calculate_future_value(years_until_retirement)
        
        # Using the 4% rule as a basic withdrawal strategy
        safe_withdrawal_rate = 0.04
        annual_withdrawal_needed = self.annual_expenses * \
            (1 + self.inflation_rate) ** years_until_retirement
        
        required_nest_egg = annual_withdrawal_needed / safe_withdrawal_rate
        
        return {
            'retirement_savings': retirement_savings,
            'required_nest_egg': required_nest_egg,
            'annual_withdrawal_needed': annual_withdrawal_needed
        }

    def is_on_track(self):
        """Determine if current savings plan meets retirement goals"""
        results = self.calculate_retirement_needs()
        return results['retirement_savings'] >= results['required_nest_egg']
