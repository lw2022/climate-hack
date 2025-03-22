import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import numpy_financial as npf
from utils import calculate_steam_price

# Page configuration
st.set_page_config(
    page_title="Low-Carbon Revenue Sharing",
    page_icon="💸",
    layout="wide"
)

# Title and introduction
st.title("💸 Low-Carbon Revenue Sharing Calculator")
st.markdown("""
This calculator determines the carbon credit revenue needed to make steam prices competitive with natural gas,
and helps optimize the revenue sharing between the corporate offtaker and Antora (technology provider).
""")

# Create sidebar for inputs
st.sidebar.header("Input Parameters")

# Steam system parameters
with st.sidebar.expander("Steam System Parameters", expanded=True):
    ng_price_per_mmbtu = st.number_input(
        "Natural Gas Price ($/MMBtu)",
        min_value=1.0,
        max_value=20.0,
        value=4.0,
        step=0.1,
        help="The cost of natural gas per MMBtu"
    )
    
    boiler_efficiency = st.slider(
        "Boiler Efficiency",
        min_value=0.50,
        max_value=0.99,
        value=0.85,
        step=0.01,
        help="The thermal efficiency of the boiler (ratio of heat transferred to steam vs. fuel energy input)"
    )
    
    bau_emissions_factor = st.number_input(
        "Business-as-usual Emissions (ton CO₂e/MMBtu)",
        min_value=0.01,
        max_value=0.1,
        value=0.053,
        step=0.001,
        format="%.4f",
        help="Business-as-usual emissions factor in metric tons of CO₂ equivalent per MMBtu"
    )
    
    project_emissions_factor = st.number_input(
        "Project Emissions (ton CO₂e/MMBtu)",
        min_value=0.0,
        max_value=0.1,
        value=0.0053,
        step=0.0001,
        format="%.4f",
        help="Project emissions factor in metric tons of CO₂ equivalent per MMBtu"
    )
    
    o_and_m_cost = st.number_input(
        "O&M Cost ($/MMBtu)",
        min_value=0.0,
        max_value=10.0,
        value=0.5,
        step=0.1,
        help="Operations and Maintenance costs per MMBtu of steam produced"
    )

# Target price and volume
with st.sidebar.expander("Pricing & Volume", expanded=True):
    target_steam_price = st.number_input(
        "Target Competitive Steam Price ($/MMBtu)",
        min_value=1.0,
        max_value=20.0,
        value=4.5,
        step=0.1,
        help="The target steam price that would be competitive for the offtaker"
    )
    
    annual_steam_usage = st.number_input(
        "Annual Steam Usage (MMBtu)",
        min_value=1000,
        max_value=1000000,
        value=100000,
        step=1000,
        help="Annual steam consumption by the offtaker"
    )

# Project financials
with st.sidebar.expander("Project Financials", expanded=True):
    capital_investment = st.number_input(
        "Initial Capital Investment ($)",
        min_value=10000,
        max_value=10000000,
        value=1000000,
        step=100000,
        help="Initial capital investment required for the project"
    )
    
    project_lifetime = st.slider(
        "Project Lifetime (Years)",
        min_value=1,
        max_value=25,
        value=10,
        step=1,
        help="Expected lifetime of the project in years"
    )
    
    discount_rate = st.slider(
        "Discount Rate (%)",
        min_value=1.0,
        max_value=20.0,
        value=8.0,
        step=0.5,
        help="Annual discount rate for NPV calculations"
    ) / 100  # Convert to decimal
    
    target_irr = st.slider(
        "Target IRR for Antora (%)",
        min_value=5.0,
        max_value=30.0,
        value=15.0,
        step=1.0,
        help="Target Internal Rate of Return for Antora"
    ) / 100  # Convert to decimal

# Calculate the required LCFS credit price to achieve target price
# First calculate steam price without LCFS
steam_price_no_lcfs = calculate_steam_price(
    ng_price_per_mmbtu=ng_price_per_mmbtu,
    boiler_efficiency=boiler_efficiency,
    lcfs_price_per_ton=0,  # No LCFS credits
    bau_emissions_factor=bau_emissions_factor,
    project_emissions_factor=project_emissions_factor,
    o_and_m_cost=o_and_m_cost
)

# Calculate avoided emissions per MMBtu
emissions_avoided = bau_emissions_factor - project_emissions_factor

# Calculate required LCFS credit price to achieve target price
price_gap = steam_price_no_lcfs - target_steam_price
required_lcfs_value_per_mmbtu = max(0, price_gap)
required_lcfs_price_per_ton = 0

if emissions_avoided > 0:
    required_lcfs_price_per_ton = required_lcfs_value_per_mmbtu / emissions_avoided

# Calculate annual LCFS revenue
annual_lcfs_revenue = required_lcfs_value_per_mmbtu * annual_steam_usage

# Calculate sensitivity analysis to determine optimal revenue split
revenue_shares_calc = np.linspace(0, 1, 21)  # 0% to 100% in 5% increments
irrs_calc = []
optimal_share_found = None

for share in revenue_shares_calc:
    antora_rev = annual_lcfs_revenue * (1 - share)
    cfs = [-capital_investment]
    for year in range(1, project_lifetime + 1):
        cfs.append(antora_rev)
    
    try:
        irr_val = npf.irr(cfs)
        # Find first revenue share that meets target IRR
        if irr_val >= target_irr and optimal_share_found is None:
            optimal_share_found = share
    except:
        pass

# Set default value based on optimal sharing to achieve target IRR
default_revenue_share = 0.5  # Default to 50% if no optimal found

if optimal_share_found is not None:
    # Use the optimal share as default
    default_revenue_share = min(optimal_share_found, 0.9)  # Capped at 90% to be reasonable

# Create a slider for revenue sharing with optimal value as default
revenue_share_offtaker_pct = st.sidebar.slider(
    "Offtaker Share of LCFS Revenue (%)",
    min_value=0,
    max_value=100,
    value=int(default_revenue_share * 100),
    step=5,
    help="Percentage of LCFS revenue that goes to the corporate offtaker"
) / 100  # Convert to decimal

# Show recommendation in sidebar
if optimal_share_found is not None:
    st.sidebar.info(f"💡 Suggested share: {optimal_share_found*100:.0f}% (to achieve target IRR)")
else:
    st.sidebar.warning("Target IRR cannot be achieved with current parameters")

# Calculate revenue shares
offtaker_annual_revenue = annual_lcfs_revenue * revenue_share_offtaker_pct
antora_annual_revenue = annual_lcfs_revenue * (1 - revenue_share_offtaker_pct)

# Calculate financial metrics for Antora
antora_cash_flows = [-capital_investment]  # Initial investment (year 0)
for year in range(1, project_lifetime + 1):
    antora_cash_flows.append(antora_annual_revenue)  # Annual revenue

# Calculate NPV and IRR
antora_npv = npf.npv(discount_rate, antora_cash_flows)
try:
    antora_irr = npf.irr(antora_cash_flows)
except:
    antora_irr = None  # IRR may not exist in some cases

# Payback period (simple)
cumulative_antora_cf = np.cumsum(antora_cash_flows)
payback_years = None
for i, cf in enumerate(cumulative_antora_cf):
    if cf >= 0:
        # Interpolate for partial year
        if i > 0:
            prev_cf = cumulative_antora_cf[i-1]
            fraction = -prev_cf / (cf - prev_cf)
            payback_years = i - 1 + fraction
        else:
            payback_years = i
        break

# Check if target IRR is achieved
irr_gap = (antora_irr - target_irr) * 100 if antora_irr is not None else None
irr_achieved = antora_irr >= target_irr if antora_irr is not None else False

# Main content layout - create two columns
col1, col2 = st.columns([3, 2])

with col1:
    # LCFS Credit Requirement
    st.header("Required Carbon Credits")
    
    # Create metrics row
    metric1, metric2, metric3 = st.columns(3)
    
    with metric1:
        st.metric(
            label="Required LCFS Price",
            value=f"${required_lcfs_price_per_ton:.2f}/ton CO₂e"
        )
    
    with metric2:
        st.metric(
            label="Annual LCFS Revenue",
            value=f"${annual_lcfs_revenue:,.2f}"
        )
    
    with metric3:
        st.metric(
            label="Emissions Avoided",
            value=f"{emissions_avoided:.4f} ton/MMBtu"
        )
    
    # Calculation explanation
    st.subheader("Calculation Breakdown")
    
    # Create a DataFrame for the calculation steps
    calc_df = pd.DataFrame([
        {"Component": "Steam Price without LCFS", "Value": f"${steam_price_no_lcfs:.2f}/MMBtu", 
         "Description": "Base steam price without carbon credits"},
        {"Component": "Target Steam Price", "Value": f"${target_steam_price:.2f}/MMBtu", 
         "Description": "Competitive target price for offtaker"},
        {"Component": "Price Gap to Fill", "Value": f"${price_gap:.2f}/MMBtu", 
         "Description": "Additional value needed from carbon credits"},
        {"Component": "Required LCFS Value", "Value": f"${required_lcfs_value_per_mmbtu:.2f}/MMBtu", 
         "Description": "Carbon credit value needed per MMBtu of steam"},
        {"Component": "Emissions Avoided", "Value": f"{emissions_avoided:.4f} ton/MMBtu", 
         "Description": "CO₂e emissions reduction per MMBtu"},
        {"Component": "Required LCFS Price", "Value": f"${required_lcfs_price_per_ton:.2f}/ton CO₂e", 
         "Description": "Required carbon credit price"}
    ])
    
    st.table(calc_df)
    
    # Revenue Sharing
    st.header("Revenue Sharing Results")
    
    # Create metrics row for revenue sharing
    share1, share2 = st.columns(2)
    
    with share1:
        st.metric(
            label=f"Offtaker Share ({revenue_share_offtaker_pct*100:.0f}%)",
            value=f"${offtaker_annual_revenue:,.2f}/year"
        )
    
    with share2:
        st.metric(
            label=f"Antora Share ({(1-revenue_share_offtaker_pct)*100:.0f}%)",
            value=f"${antora_annual_revenue:,.2f}/year"
        )
    
    # Pie chart for revenue distribution
    fig_pie = go.Figure(data=[go.Pie(
        labels=[f'Offtaker ({revenue_share_offtaker_pct*100:.0f}%)', 
                f'Antora ({(1-revenue_share_offtaker_pct)*100:.0f}%)'],
        values=[offtaker_annual_revenue, antora_annual_revenue],
        hole=.4,
        marker_colors=['#4BC0C0', '#FF9900']
    )])
    
    fig_pie.update_layout(
        title="Annual LCFS Revenue Distribution",
        height=400,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Financial metrics for Antora
    st.header("Antora Financial Metrics")
    
    # Highlight if IRR target is achieved
    if irr_achieved:
        st.success(f"✅ Target IRR of {target_irr*100:.1f}% is achieved!")
    else:
        st.error(f"❌ Target IRR of {target_irr*100:.1f}% is not achieved. Consider adjusting the revenue share.")
    
    # Display financial metrics
    fin1, fin2, fin3 = st.columns(3)
    
    with fin1:
        st.metric(
            label="Antora NPV",
            value=f"${antora_npv:,.2f}"
        )
    
    with fin2:
        st.metric(
            label="Antora IRR",
            value=f"{antora_irr*100:.2f}%" if antora_irr is not None else "N/A",
            delta=f"{irr_gap:.2f}%" if irr_gap is not None else None,
            delta_color="normal"
        )
    
    with fin3:
        st.metric(
            label="Payback Period",
            value=f"{payback_years:.2f} years" if payback_years is not None else "N/A"
        )
    
    # Revenue Share Optimization
    st.subheader("Revenue Share Optimization")
    
    # Calculate optimal revenue share for target IRR
    if antora_irr is not None:
        # Run sensitivity analysis on revenue share percentage
        revenue_shares = np.linspace(0, 1, 21)  # 0% to 100% in 5% increments
        irrs = []
        npvs = []
        
        for share in revenue_shares:
            antora_rev = annual_lcfs_revenue * (1 - share)
            cfs = [-capital_investment]
            for year in range(1, project_lifetime + 1):
                cfs.append(antora_rev)
            
            try:
                irr_val = npf.irr(cfs)
                irrs.append(irr_val * 100)  # Convert to percentage
            except:
                irrs.append(None)
            
            npv_val = npf.npv(discount_rate, cfs)
            npvs.append(npv_val)
        
        # Find optimal revenue share
        optimal_share = None
        for i, (share, irr_val) in enumerate(zip(revenue_shares, irrs)):
            if irr_val is not None and irr_val >= target_irr * 100:
                optimal_share = share
                break
        
        # Create sensitivity chart
        sensitivity_data = pd.DataFrame({
            "offtaker_share": [s * 100 for s in revenue_shares],  # Convert to percentages for display
            "antora_irr": irrs,
            "antora_npv": npvs
        }).dropna()
        
        if not sensitivity_data.empty:
            # IRR sensitivity chart
            fig_irr = px.line(
                sensitivity_data,
                x="offtaker_share",
                y="antora_irr",
                labels={
                    "offtaker_share": "Offtaker Revenue Share (%)",
                    "antora_irr": "Antora IRR (%)"
                },
                title="Antora IRR vs. Revenue Share"
            )
            
            # Add target IRR line
            fig_irr.add_hline(
                y=target_irr * 100,
                line_dash="dash",
                line_color="red",
                annotation_text="Target IRR",
                annotation_position="bottom right"
            )
            
            # Add current value indicator
            fig_irr.add_vline(
                x=revenue_share_offtaker_pct * 100,
                line_dash="dash",
                line_color="gray",
                annotation_text="Current",
                annotation_position="top right"
            )
            
            fig_irr.update_layout(
                height=300,
                yaxis=dict(
                    title="IRR (%)",
                    gridcolor='rgba(220, 220, 220, 0.6)',
                ),
                xaxis=dict(
                    gridcolor='rgba(220, 220, 220, 0.6)',
                ),
                plot_bgcolor='rgba(0, 0, 0, 0)',
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig_irr, use_container_width=True)
            
            # Add recommendation
            if optimal_share is not None:
                st.info(f"💡 Recommendation: Maximum offtaker share to achieve target IRR: {optimal_share*100:.0f}%")
            else:
                st.warning("⚠️ Target IRR cannot be achieved with current parameters.")
        
    # Additional Insights
    st.subheader("Key Insights")
    
    # Calculate some additional insights
    total_lcfs_revenue_project_life = annual_lcfs_revenue * project_lifetime
    total_antora_revenue = antora_annual_revenue * project_lifetime
    roi = (total_antora_revenue / capital_investment - 1) * 100 if capital_investment > 0 else float('inf')
    
    insights = [
        f"Total LCFS revenue over project life: ${total_lcfs_revenue_project_life:,.2f}",
        f"Total Antora revenue over project life: ${total_antora_revenue:,.2f}",
        f"Return on Investment (ROI): {roi:.2f}%",
        f"Equivalent carbon price breakeven: ${required_lcfs_price_per_ton:.2f}/ton CO₂e"
    ]
    
    for insight in insights:
        st.markdown(f"• {insight}")

# Methodology and explanation
st.header("Methodology")
with st.expander("Carbon Revenue & Sharing Methodology"):
    st.markdown("""
    ### Low-Carbon Revenue Sharing Calculation
    
    The low-carbon revenue sharing model is calculated using the following steps:
    
    1. **Required Carbon Credit Value Calculation**
       - Calculate steam price without carbon credits
       - Determine price gap between no-carbon price and target competitive price
       - Calculate required carbon credit value per MMBtu to fill the gap
    
    2. **Required Carbon Credit Price Calculation**
       - Emissions avoided (tons CO₂e/MMBtu) = Business-as-usual Emissions - Project Emissions
       - Required carbon credit price ($/ton CO₂e) = Required value per MMBtu / Emissions avoided
    
    3. **Annual Revenue Calculation**
       - Annual LCFS revenue ($) = Required carbon credit value per MMBtu × Annual steam usage
    
    4. **Revenue Sharing Calculation**
       - Offtaker share ($) = Annual LCFS revenue × Offtaker share percentage
       - Antora share ($) = Annual LCFS revenue × (1 - Offtaker share percentage)
    
    5. **Financial Metrics Calculation**
       - Antora NPV: Net Present Value of Antora cash flows (initial investment + annual shares)
       - Antora IRR: Internal Rate of Return for Antora
       - Payback Period: Time required for Antora to recover the initial investment
       - Optimal Revenue Share: Maximum offtaker share that still allows Antora to achieve target IRR
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Steam Price Calculator | Developed with Streamlit")