import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Retirement Withdrawal Calculator",
    page_icon="💰"
)

# Function to detect current theme
def get_current_theme():
    container = st.container()
    bg_color = st.get_option("theme.backgroundColor")
    container.empty()
    return "light" if bg_color == "white" else "dark"

# Helper functions
def parse_currency(value):
    if isinstance(value, (int, float)):
        return value
    value = value.replace('$', '').replace(',', '')
    try:
        return float(value)
    except ValueError:
        return None

def format_currency(value):
    return f"${value:,.0f}"

def calculate_retirement(initial_capital, withdrawal_rate, annual_expenses, years, return_rate, inflation_rate, tax_rate, taxable_percentage):
    capital = [initial_capital]
    expenses = [annual_expenses]
    withdrawals = [max(annual_expenses, initial_capital * (withdrawal_rate / 100))]
    for year in range(1, years + 1):
        current_expenses = expenses[-1] * (1 + inflation_rate/100)
        expenses.append(current_expenses)
        
        current_withdrawal = withdrawals[-1] * (1 + inflation_rate/100)
        withdrawals.append(current_withdrawal)
        
        withdrawal = max(current_expenses, current_withdrawal)
        
        growth = capital[-1] * (return_rate / 100)
        tax = growth * (taxable_percentage / 100) * (tax_rate / 100)
        
        new_capital = capital[-1] + growth - tax - withdrawal
        capital.append(max(0, new_capital))
        
        if new_capital <= 0:
            break
    return capital, expenses, withdrawals

def find_sustainable_value(target_years, annual_expenses, return_rate, inflation_rate, tax_rate, taxable_percentage, find_capital=True, initial_value=1000000, withdrawal_rate=4):
    low, high = 0, initial_value * 10 if find_capital else 20
    while high - low > (1 if find_capital else 0.01):
        mid = (low + high) / 2
        if find_capital:
            capital, _, _ = calculate_retirement(mid, withdrawal_rate, annual_expenses, target_years, return_rate, inflation_rate, tax_rate, taxable_percentage)
        else:
            capital, _, _ = calculate_retirement(initial_value, mid, annual_expenses, target_years, return_rate, inflation_rate, tax_rate, taxable_percentage)
        if len(capital) > target_years:
            high = mid
        else:
            low = mid
    return high

# Title and description
st.title('💰 Retirement Withdrawal Calculator')
st.markdown("""
    This calculator helps you estimate how long your retirement savings will last based on your initial capital, annual expenses, and other financial parameters.
    Adjust the inputs to see how different scenarios affect your retirement plan.
""")

# Input section
st.sidebar.header("Input Parameters")
initial_capital_input = st.sidebar.text_input(
    'Initial Capital',
    value="$500,000",
    help="Enter the initial capital amount. You can use dollar signs and commas."
)
initial_capital = parse_currency(initial_capital_input)
if initial_capital is None:
    st.sidebar.error("Please enter a valid dollar amount for Initial Capital")
    initial_capital = 500000

annual_expenses_input = st.sidebar.text_input(
    'Annual Expenses',
    value="$75,000",
    help="Enter your annual expenses. You can use dollar signs and commas."
)
annual_expenses = parse_currency(annual_expenses_input)
if annual_expenses is None:
    st.sidebar.error("Please enter a valid dollar amount for Annual Expenses")
    annual_expenses = 75000

withdrawal_rate = st.sidebar.slider('Annual Withdrawal Rate (%)', 0.0, 10.0, 4.0, 0.1, help="The percentage of your initial capital you plan to withdraw annually.")
return_rate = st.sidebar.slider('Expected Annual Return (%)', 0.0, 15.0, 10.0, 0.1, help="The expected annual return on your investments.")
inflation_rate = st.sidebar.slider('Expected Annual Inflation (%)', 0.0, 10.0, 3.8, 0.1, help="The expected annual inflation rate.")
tax_rate = st.sidebar.slider('Tax Rate (%)', 0.0, 50.0, 15.0, 0.1, help="The tax rate applied to your investment returns.")
taxable_percentage = st.sidebar.slider('Percentage of Capital Subject to Tax (%)', 0.0, 100.0, 50.0, 0.1, help="The percentage of your capital that is subject to tax.")

# Calculation
years = 50
capital_over_time, expenses_over_time, withdrawals_over_time = calculate_retirement(initial_capital, withdrawal_rate, annual_expenses, years, return_rate, inflation_rate, tax_rate, taxable_percentage)

# Results section
st.header("Results")

# Plot
current_theme = get_current_theme()
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(len(capital_over_time))), y=capital_over_time, mode='lines', name='Capital'))
fig.add_trace(go.Scatter(x=list(range(len(expenses_over_time))), y=expenses_over_time, mode='lines', name='Annual Expenses'))
fig.add_trace(go.Scatter(x=list(range(len(withdrawals_over_time))), y=withdrawals_over_time, mode='lines', name='Annual Withdrawal'))
fig.update_layout(
    title='Projected Capital, Expenses, and Withdrawals Over Time',
    xaxis_title='Years',
    yaxis_title='Amount ($)',
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='black' if current_theme == 'light' else 'white'),
    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),  # Move legend below the plot
    margin=dict(l=50, r=20, t=80, b=100),  # Adjust bottom margin for legend
    autosize=True
)
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey' if current_theme == 'light' else 'grey')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey' if current_theme == 'light' else 'grey')
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Table
st.subheader("Detailed Results")
intervals = [0, 10, 20, 30, 40, 50]
data = {
    'Years': intervals,
    'Remaining Capital': [f'${capital_over_time[year]:,.0ßf}' if year < len(capital_over_time) else 'N/A' for year in intervals],
    'Annual Expenses': [f'${expenses_over_time[year]:,.0f}' if year < len(expenses_over_time) else 'N/A' for year in intervals],
    'Annual Withdrawal': [f'${withdrawals_over_time[year]:,.0f}' if year < len(withdrawals_over_time) else 'N/A' for year in intervals]
}
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True, height=300)

# Analysis
st.subheader("Analysis")
years_until_depletion = len(capital_over_time) - 1
if years_until_depletion < years:
    st.warning(f'⚠️ Warning: Capital depleted after {years_until_depletion} years.')
    
    # Calculate required initial capital for 50 years
    required_capital_50y = find_sustainable_value(50, annual_expenses, return_rate, inflation_rate, tax_rate, taxable_percentage, True, initial_capital, withdrawal_rate)
    st.info(f'💡 Required initial capital for 50 years: ${required_capital_50y:,.2f}')
    
    # Calculate maximum sustainable withdrawal rate for 50 years
    max_withdrawal_rate_50y = find_sustainable_value(50, annual_expenses, return_rate, inflation_rate, tax_rate, taxable_percentage, False, initial_capital, withdrawal_rate)
    st.info(f'💡 Maximum sustainable withdrawal rate for 50 years: {max_withdrawal_rate_50y:.2f}%')
    
    # Calculate maximum sustainable annual expenses for 50 years
    max_expenses_50y = max_withdrawal_rate_50y * initial_capital / 100
    st.info(f'💡 Maximum sustainable initial annual expenses for 50 years: ${max_expenses_50y:,.2f}')
else:
    st.success(f'✅ Capital lasts for the entire {years} year period.')
    
    # Calculate remaining capital after 50 years
    final_capital = capital_over_time[-1]
    st.info(f'💡 Remaining capital after 50 years: ${final_capital:,.2f}')
    
    # Calculate total withdrawals over 50 years
    total_withdrawals = sum(expenses_over_time)
    st.info(f'💡 Total withdrawals over 50 years: ${total_withdrawals:,.2f}')

# Perpetuity calculations
st.subheader('Perpetuity Calculations')
real_return_rate = return_rate - inflation_rate
after_tax_real_return_rate = real_return_rate * (1 - (tax_rate / 100) * (taxable_percentage / 100))
sustainable_withdrawal = initial_capital * (after_tax_real_return_rate / 100)
st.info(f"💡 Sustainable annual withdrawal in perpetuity: ${sustainable_withdrawal:,.2f}")
perpetuity_withdrawal_rate = (sustainable_withdrawal / initial_capital) * 100
st.info(f"💡 Sustainable withdrawal rate in perpetuity: {perpetuity_withdrawal_rate:.2f}%")
required_capital_perpetuity = annual_expenses / (after_tax_real_return_rate / 100)
st.info(f"💡 Required initial capital for perpetuity (based on current annual expenses): ${required_capital_perpetuity:,.2f}")

# Footer
st.markdown("""
    ---
    **Note:** This calculator provides estimates based on the inputs provided. Actual results may vary based on market conditions and other factors.
""")

# Custom CSS for responsiveness
st.markdown("""
<style>
@media (max-width: 768px) {
    .stApp {
        padding-top: 1rem;
    }
    .stPlotlyChart {
        height: 60vh !important;
    }
}
@media (max-width: 480px) {
    .stPlotlyChart {
        height: 70vh !important;
    }
}
</style>
""", unsafe_allow_html=True)
