import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import calculate_steam_price, perform_sensitivity_analysis

# Page configuration
st.set_page_config(
    page_title="Steam Price Calculator",
    page_icon="♨️",
    layout="wide"
)

# Title and introduction
st.title("♨️ Steam Price Calculator")
st.markdown("""
This calculator helps you determine the price of steam based on various factors including natural gas costs, 
boiler efficiency, Low Carbon Fuel Standard (LCFS) credits, and emissions factors.

👈 **Check out the "LCFS Revenue Sharing" page** in the sidebar to optimize revenue sharing between offtakers and Antora.
""")

# Create sidebar for inputs
st.sidebar.header("Input Parameters")

# Natural gas price input
ng_price_per_mmbtu = st.sidebar.number_input(
    "Natural Gas Price ($/MMBtu)",
    min_value=0.0,
    max_value=50.0,
    value=4.0,
    step=0.1,
    help="The cost of natural gas per MMBtu (Million British Thermal Units)"
)

# Boiler efficiency input
boiler_efficiency = st.sidebar.slider(
    "Boiler Efficiency",
    min_value=0.50,
    max_value=0.99,
    value=0.85,
    step=0.01,
    help="The thermal efficiency of the boiler (ratio of heat transferred to steam vs. fuel energy input)"
)

# LCFS price input
lcfs_price_per_ton = st.sidebar.number_input(
    "LCFS Price ($/ton CO₂e)",
    min_value=0.0,
    max_value=1000.0,
    value=100.0,
    step=5.0,
    help="The price of Low Carbon Fuel Standard credits per metric ton of CO₂ equivalent"
)

# Emissions factors
st.sidebar.subheader("Emissions Factors")
bau_emissions_factor = st.sidebar.number_input(
    "Business-as-usual Emissions (ton CO₂e/MMBtu)",
    min_value=0.0,
    max_value=1.0,
    value=0.053,
    step=0.001,
    format="%.4f",
    help="Business-as-usual emissions factor in metric tons of CO₂ equivalent per MMBtu"
)

project_emissions_factor = st.sidebar.number_input(
    "Project Emissions (ton CO₂e/MMBtu)",
    min_value=0.0,
    max_value=1.0,
    value=0.0053,
    step=0.0001,
    format="%.4f",
    help="Project emissions factor in metric tons of CO₂ equivalent per MMBtu"
)

# O&M cost input
o_and_m_cost = st.sidebar.number_input(
    "O&M Cost ($/MMBtu)",
    min_value=0.0,
    max_value=10.0,
    value=0.5,
    step=0.1,
    help="Operations and Maintenance costs per MMBtu of steam produced"
)

# Calculate steam price
result = calculate_steam_price(
    ng_price_per_mmbtu=ng_price_per_mmbtu,
    boiler_efficiency=boiler_efficiency,
    lcfs_price_per_ton=lcfs_price_per_ton,
    bau_emissions_factor=bau_emissions_factor,
    project_emissions_factor=project_emissions_factor,
    o_and_m_cost=o_and_m_cost,
    return_components=True  # Get detailed cost breakdown
)

# Extract components from result
net_steam_price = result["net_steam_price"]
fuel_cost = result["fuel_cost"]
lcfs_credit = result["lcfs_credit"]
emissions_avoided = result["emissions_avoided"]

# Main content layout - create two columns
col1, col2 = st.columns([3, 2])

with col1:
    # Results section
    st.header("Calculated Steam Price")
    
    # Create metrics row
    metric1, metric2, metric3 = st.columns(3)
    
    with metric1:
        st.metric(
            label="Net Steam Price",
            value=f"${net_steam_price:.2f}/MMBtu"
        )
    
    with metric2:
        st.metric(
            label="Fuel Cost",
            value=f"${fuel_cost:.2f}/MMBtu"
        )
    
    with metric3:
        st.metric(
            label="LCFS Credit",
            value=f"${lcfs_credit:.2f}/MMBtu"
        )
    
    # Calculation breakdown
    st.subheader("Calculation Breakdown")
    
    # Add toggle for showing original units
    show_original_units = st.checkbox("Show values in original units", value=False)
    
    if show_original_units:
        # Create a DataFrame with original units
        calc_df = pd.DataFrame([
            {"Component": "Natural Gas Price", "Value": f"${ng_price_per_mmbtu:.2f}/MMBtu", "Original Unit": "$/MMBtu"},
            {"Component": "Boiler Efficiency", "Value": f"{boiler_efficiency:.2f}", "Original Unit": "Decimal (0-1)"},
            {"Component": "LCFS Price", "Value": f"${lcfs_price_per_ton:.2f}/ton CO₂e", "Original Unit": "$/ton CO₂e"},
            {"Component": "Business-as-usual Emissions", "Value": f"{bau_emissions_factor:.4f}", "Original Unit": "ton CO₂e/MMBtu"},
            {"Component": "Project Emissions", "Value": f"{project_emissions_factor:.4f}", "Original Unit": "ton CO₂e/MMBtu"},
            {"Component": "O&M Cost", "Value": f"${o_and_m_cost:.2f}/MMBtu", "Original Unit": "$/MMBtu"},
            {"Component": "Required Natural Gas", "Value": f"{result['required_ng_per_mmbtu_steam']:.4f}", "Original Unit": "MMBtu gas/MMBtu steam"},
            {"Component": "Emissions Avoided", "Value": f"{emissions_avoided:.4f}", "Original Unit": "ton CO₂e/MMBtu"}
        ])
        st.dataframe(calc_df)
    
    # Always show calculation steps
    calc_steps_df = pd.DataFrame([
        {"Component": "Fuel Cost", "Value": f"${fuel_cost:.2f}/MMBtu", "Description": f"Natural gas price (${ng_price_per_mmbtu:.2f}/MMBtu) ÷ boiler efficiency ({boiler_efficiency:.2f})"},
        {"Component": "LCFS Credit", "Value": f"-${lcfs_credit:.2f}/MMBtu", "Description": f"Emissions avoided ({emissions_avoided:.4f} tons/MMBtu) × LCFS price (${lcfs_price_per_ton:.2f}/ton)"},
        {"Component": "O&M Cost", "Value": f"${o_and_m_cost:.2f}/MMBtu", "Description": "Operations and maintenance costs"},
        {"Component": "Net Steam Price", "Value": f"${net_steam_price:.2f}/MMBtu", "Description": "Fuel cost - LCFS credit + O&M cost"}
    ])
    
    st.table(calc_steps_df)
    
    # Cost Breakdown Chart
    st.subheader("Cost Breakdown")
    
    # Prepare data for chart
    labels = ['Fuel Cost', 'LCFS Credit (Savings)', 'O&M Cost', 'Net Price']
    values = [fuel_cost, -lcfs_credit, o_and_m_cost, net_steam_price]
    colors = ['#FF9900', '#36A2EB', '#FFCE56', '#4BC0C0']
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name="Steam Price Components",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=labels,
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#FF9900"}},
        decreasing={"marker": {"color": "#36A2EB"}},
        totals={"marker": {"color": "#4BC0C0"}}
    ))
    
    fig.update_layout(
        title="Steam Price Waterfall Chart",
        showlegend=False,
        height=400,
        yaxis=dict(
            title="$/MMBtu",
            gridcolor='rgba(220, 220, 220, 0.6)',
        ),
        xaxis=dict(
            title="Components",
            gridcolor='rgba(220, 220, 220, 0.6)',
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=50, r=50),
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Sensitivity Analysis
    st.header("Sensitivity Analysis")
    st.markdown("See how changes in key parameters affect the steam price:")
    
    # Select parameter for sensitivity analysis
    sensitivity_param = st.selectbox(
        "Select Parameter to Analyze",
        ["Natural Gas Price", "Boiler Efficiency", "LCFS Price", "O&M Cost"]
    )
    
    # Perform sensitivity analysis
    param_map = {
        "Natural Gas Price": "ng_price_per_mmbtu",
        "Boiler Efficiency": "boiler_efficiency",
        "LCFS Price": "lcfs_price_per_ton",
        "O&M Cost": "o_and_m_cost"
    }
    
    # Set range for sensitivity analysis
    if sensitivity_param == "Natural Gas Price":
        param_range = np.linspace(ng_price_per_mmbtu * 0.5, ng_price_per_mmbtu * 1.5, 11)
        x_label = "Natural Gas Price ($/MMBtu)"
    elif sensitivity_param == "Boiler Efficiency":
        param_range = np.linspace(max(0.5, boiler_efficiency * 0.8), min(0.99, boiler_efficiency * 1.2), 11)
        x_label = "Boiler Efficiency"
    elif sensitivity_param == "LCFS Price":
        param_range = np.linspace(max(0, lcfs_price_per_ton * 0.5), lcfs_price_per_ton * 1.5, 11)
        x_label = "LCFS Price ($/ton CO₂e)"
    else:  # O&M Cost
        param_range = np.linspace(max(0, o_and_m_cost * 0.5), o_and_m_cost * 1.5, 11)
        x_label = "O&M Cost ($/MMBtu)"
    
    # Run sensitivity analysis
    sensitivity_results = perform_sensitivity_analysis(
        param_name=param_map[sensitivity_param],
        param_range=param_range,
        fixed_params={
            "ng_price_per_mmbtu": ng_price_per_mmbtu,
            "boiler_efficiency": boiler_efficiency,
            "lcfs_price_per_ton": lcfs_price_per_ton,
            "bau_emissions_factor": bau_emissions_factor,
            "project_emissions_factor": project_emissions_factor,
            "o_and_m_cost": o_and_m_cost
        }
    )
    
    # Create sensitivity chart
    fig_sensitivity = px.line(
        sensitivity_results,
        x="param_value",
        y="steam_price",
        labels={
            "param_value": x_label,
            "steam_price": "Steam Price ($/MMBtu)"
        },
        title=f"Sensitivity of Steam Price to {sensitivity_param}"
    )
    
    # Add current value indicator
    if sensitivity_param == "Natural Gas Price":
        current_value = ng_price_per_mmbtu
    elif sensitivity_param == "Boiler Efficiency":
        current_value = boiler_efficiency
    elif sensitivity_param == "LCFS Price":
        current_value = lcfs_price_per_ton
    else:  # O&M Cost
        current_value = o_and_m_cost
    
    # Get y-value at current x-value (approximate)
    current_y = net_steam_price
    
    fig_sensitivity.add_scatter(
        x=[current_value],
        y=[current_y],
        mode="markers",
        marker=dict(color="red", size=10),
        name="Current Value",
        hoverinfo="text",
        text=f"Current: ({current_value:.2f}, ${current_y:.2f})"
    )
    
    fig_sensitivity.update_layout(
        height=400,
        yaxis=dict(
            title="Steam Price ($/MMBtu)",
            gridcolor='rgba(220, 220, 220, 0.6)',
        ),
        xaxis=dict(
            gridcolor='rgba(220, 220, 220, 0.6)',
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(t=50, b=50, l=50, r=50),
    )
    
    st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # Explanation of sensitivity analysis
    st.markdown("""
    **How to interpret:** 
    
    This chart shows how the steam price changes when varying a single parameter while keeping all other parameters constant.
    The red dot indicates the current value based on your inputs.
    """)

# Methodology and explanation
st.header("Methodology")
with st.expander("Calculation Methodology"):
    st.markdown("""
    ### Steam Price Calculation Formula

    The steam price is calculated using the following steps:

    1. **Fuel Cost Calculation**
       - Required natural gas per MMBtu of steam = 1 / Boiler Efficiency
       - Fuel cost ($/MMBtu) = Natural Gas Price ($/MMBtu) × Required natural gas per MMBtu of steam

    2. **Emissions Avoided Calculation**
       - Emissions avoided (tons CO₂e/MMBtu) = Business-as-usual Emissions Factor - Project Emissions Factor

    3. **LCFS Credit Calculation**
       - LCFS credit ($/MMBtu) = Emissions avoided (tons CO₂e/MMBtu) × LCFS price ($/ton CO₂e)

    4. **Net Steam Price Calculation**
       - Net steam price ($/MMBtu) = Fuel cost - LCFS credit + O&M cost
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Steam Price Calculator | Developed with Streamlit")
