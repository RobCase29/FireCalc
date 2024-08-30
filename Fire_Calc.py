import streamlit as st
import plotly.graph_objects as go
import pandas as pd

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

    <script>
        function updateColors() {
            const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            document.body.style.setProperty('--background-color', isDarkMode ? '#1e1e1e' : '#ffffff');
            document.body.style.setProperty('--secondary-background-color', isDarkMode ? '#2e3b4e' : '#f0f2f6');
            document.body.style.setProperty('--text-color', isDarkMode ? '#ffffff' : '#000000');
            document.body.style.setProperty('--input-background-color', isDarkMode ? '#3e4c5e' : '#ffffff');
        }

        updateColors();
        window.matchMedia('(prefers-color-scheme: dark)').addListener(updateColors);
    </script>
""", unsafe_allow_html=True)

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
    value="$1,000,000",
    help="Enter the initial capital amount. You can use dollar signs and commas."
)
initial_capital = parse_currency(initial_capital_input)
if initial_capital is None:
    st.sidebar.error("Please enter a valid dollar amount for Initial Capital")
    initial_capital = 1000000

annual_expenses_input = st.sidebar.text_input(
    'Annual Expenses',
    value="$40,000",
    help="Enter your annual expenses. You can use dollar signs and commas."
)
annual_expenses = parse_currency(annual_expenses_input)
if annual_expenses is None:
    st.sidebar.error("Please enter a valid dollar amount for Annual Expenses")
    annual_expenses = 40000

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
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(len(capital_over_time))), y=capital_over_time, mode='lines', name='Capital'))
fig.add_trace(go.Scatter(x=list(range(len(expenses_over_time))), y=expenses_over_time, mode='lines', name='Annual Expenses'))
fig.add_trace(go.Scatter(x=list(range(len(withdrawals_over_time))), y=withdrawals_over_time, mode='lines', name='Annual Withdrawal'))
fig.update_layout(title='Projected Capital, Expenses, and Withdrawals Over Time', xaxis_title='Years', yaxis_title='Amount ($)', height=500, plot_bgcolor='var(--background-color)', paper_bgcolor='var(--background-color)', font=dict(color='var(--text-color)'))
st.plotly_chart(fig, use_container_width=True)

# Table
intervals = [0, 10, 20, 30, 40, 50]
data = {
    'Years': intervals,
    'Remaining Capital': [f'${capital_over_time[year]:,.2f}' if year < len(capital_over_time) else 'N/A' for year in intervals],
    'Annual Expenses': [f'${expenses_over_time[year]:,.2f}' if year < len(expenses_over_time) else 'N/A' for year in intervals],
    'Annual Withdrawal': [f'${withdrawals_over_time[year]:,.2f}' if year < len(withdrawals_over_time) else 'N/A' for year in intervals]
}
df = pd.DataFrame(data)
st.table(df)

# Analysis
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

# Calculate the real rate of return (after inflation and taxes)
real_return_rate = return_rate - inflation_rate
after_tax_real_return_rate = real_return_rate * (1 - (tax_rate / 100) * (taxable_percentage / 100))

# Calculate the sustainable withdrawal amount in perpetuity
sustainable_withdrawal = initial_capital * (after_tax_real_return_rate / 100)

st.info(f"💡 Sustainable annual withdrawal in perpetuity: ${sustainable_withdrawal:,.2f}")

# Calculate the withdrawal rate as a percentage of initial capital
perpetuity_withdrawal_rate = (sustainable_withdrawal / initial_capital) * 100
st.info(f"💡 Sustainable withdrawal rate in perpetuity: {perpetuity_withdrawal_rate:.2f}%")

# Calculate required initial capital for perpetuity based on current annual expenses
required_capital_perpetuity = annual_expenses / (after_tax_real_return_rate / 100)
st.info(f"💡 Required initial capital for perpetuity (based on current annual expenses): ${required_capital_perpetuity:,.2f}")

# Compare current withdrawal to sustainable withdrawal
current_withdrawal = max(annual_expenses, initial_capital * (withdrawal_rate / 100))
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
