import streamlit as st
import plotly.graph_objects as go
from PIL import Image
import base64

st.set_page_config(page_title="Green Station Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    [data-testid="stToolbar"] {
        background-color: #f1f9e1 !important;
    }
    .stApp {
        background-color:#f1f9e1;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color:#637b37;
    }
    .metric-unit {
        font-size: 16px;
        color: #666;
    }
    [data-testid="stSidebar"] {
        background-color:#c2e875;
    }
    .stSlider {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.title("Project Inputs")
monthly = st.sidebar.number_input("Monthly Air-Conditioning Energy Consumption Cost ($)", value=150000)
stations = st.sidebar.number_input("Number of Stations", 1, 100, 1)
capex = st.sidebar.number_input("CAPEX (One-time cost)", min_value=0.0, value=15000.0, step=1.00)
opex = st.sidebar.number_input("OPEX (Yearly cost)", min_value=0.0, value=5000.0)
electricity_tariff = st.sidebar.number_input("Electricity Tariff ($/kWh)", min_value=0.0, value=0.15, step=0.01)
flat = st.sidebar.number_input("4-room flat consumption (kWh)", min_value=0.0, value=4000.0, step=0.1)
trees = st.sidebar.number_input("Trees consumption (kWh)", min_value=0.0, value=52.5, step=0.1)

st.sidebar.markdown("#### Potential range of Percentage Savings")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_savings = st.number_input("Lowest (%)", min_value=0, max_value=100, value=5, step=1)
with col2:
    end_savings = st.number_input("Highest (%)", min_value=0, max_value=100, value=10, step=1)
if end_savings < start_savings:
    end_savings = start_savings

# main content
col1, col2 = st.columns([2, 1])  # Adjust the ratio as needed

with col1:
    st.markdown("<h1 style='text-align: left; font-size: 40px;'>Sustainability Project Evaluation Dashboard</h1>", unsafe_allow_html=True)
    if start_savings == end_savings:
        savings_percentage = start_savings  # if they're equal, just use that value
        st.markdown(f"""
                <p style='font-size: 24px; font-weight: bold; color: #637b37;'>
                    Savings Percentage: {savings_percentage}%
                </p>
            """, unsafe_allow_html=True)
    else:
        # savings percentage slider
        st.markdown("""
            <style>
            .reduce-spacing {
                margin-bottom: -50px;  /* Adjust this value to control the spacing */
            }
            </style>
            <h5 class='reduce-spacing'>Adjust Potential Savings Percentage</h5>
        """, unsafe_allow_html=True)

        savings_percentage = st.slider("Savings Percentage",
                                       min_value=start_savings,
                                       max_value=end_savings,
                                       value=start_savings,
                                       step=1)

with col2:
    image = Image.open('dashboard.png')
    st.markdown(
        f"""
            <div style="display: flex; justify-content: flex-end;">
                <img src="data:image/png;base64,{base64.b64encode(open('dashboard.png', 'rb').read()).decode()}" 
                     style="width: 100%; height: 230px; transform: scale(1.2, 0.9);">
            </div>
            """,
        unsafe_allow_html=True
    )


# metrics calculation
annual_savings = int(monthly * 12 * stations * (savings_percentage / 100))
energy_savings = int((monthly * 12 * (savings_percentage / 100) * stations) / electricity_tariff)
flats_equivalent = energy_savings / 4000
trees_equivalent = energy_savings / 52.5
roi = ((annual_savings * 15) / (capex + opex * 15)) * 100
payback = capex / (annual_savings - opex) if annual_savings > opex else "infinite years"

# metrics display, with savings ($ and energy), roi gains and payback period
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annual Savings</div>
        <div class="metric-value">${annual_savings:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annual Energy Savings</div>
        <div class="metric-value">{energy_savings:,}<span class="metric-unit"> kWh</span></div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">ROI Gains (15 Years)</div>
        <div class="metric-value">{roi:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Payback Period</div>
        <div class="metric-value">{payback if isinstance(payback, str) else f"{payback:.1f} years"}</div>
    </div>
    """, unsafe_allow_html=True)

# flats and trees equivalent
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Energy Savings Equivalent to</div>
        <div class="metric-value">{flats_equivalent:.1f} 4-room flats</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">CO2 Reduction Saves</div>
        <div class="metric-value">{trees_equivalent:.0f} trees</div>
    </div>
    """, unsafe_allow_html=True)

# for plots
col1, col2, col3 = st.columns(3)


def calculate_roi(savings_percentage):
    annual_savings = monthly * 12 * stations * (savings_percentage / 100)
    return ((annual_savings * 15) / (capex + opex * 15)) * 100


def calculate_payback(savings_percentage):
    annual_savings = monthly * 12 * stations * (savings_percentage / 100)
    if annual_savings > opex:
        return capex / (annual_savings - opex)
    else:
        return "Infinite"


def calculate_annual(savings_percentage):
    annual_savings = monthly*12*stations*(savings_percentage/100)
    return annual_savings


savings_percentages = list(range(start_savings, end_savings + 1))
roi_values = [calculate_roi(sp) for sp in savings_percentages]
payback_values = [calculate_payback(sp) for sp in savings_percentages]
annual_values = [calculate_annual(sp) for sp in savings_percentages]

# ROI graph
with col1:
    fig_roi = go.Figure(data=[go.Scatter(x=savings_percentages, y=roi_values, mode='lines+markers', line=dict(color='#637b37', width=2), marker=dict(color='#637b37', size=6))])
    fig_roi.update_layout(
        title="ROI vs Percentage Savings",
        xaxis_title="Percentage Savings",
        yaxis_title="ROI (%)",
        height=400
    )
    st.plotly_chart(fig_roi, use_container_width=True)

# payback graph
with col2:
    fig_payback = go.Figure(data=[go.Scatter(x=savings_percentages, y=payback_values, mode='lines+markers', line=dict(color='#637b37', width=2), marker=dict(color='#637b37', size=6))])
    fig_payback.update_layout(
        title="Payback Period vs Percentage Savings",
        xaxis_title="Percentage Savings",
        yaxis_title="Years",
        height=400
    )
    fig_payback.update_yaxes(range=[0, 20])  # Limit to 20 years
    st.plotly_chart(fig_payback, use_container_width=True)

# annual savings graph
with col3:
    fig_annual = go.Figure(data=[go.Scatter(x=savings_percentages, y=annual_values, mode='lines+markers', line=dict(color='#637b37', width=2),marker=dict(color='#637b37', size=6))])
    fig_annual.update_layout(
        title="Annual Savings vs Percentage Savings",
        xaxis_title="Percentage Savings",
        yaxis_title="Annual Savings",
        height=400
    )
    st.plotly_chart(fig_annual, use_container_width=True)
