import pandas as pd
import numpy as np
import numpy_financial as npf

def calculate_steam_price(
    ng_price_per_mmbtu=4.00,
    boiler_efficiency=0.85,
    lcfs_price_per_ton=100,
    bau_emissions_factor=0.053,    # in metric tons CO₂e per MMBtu
    project_emissions_factor=0.0053,
    o_and_m_cost=0.50,
    return_components=False
):
    """
    Calculate steam price ($/MMBtu) based on:
    - Natural gas cost
    - Boiler efficiency
    - LCFS carbon credit based on avoided CO₂e emissions
    - Optional O&M costs

    Args:
        ng_price_per_mmbtu (float): Natural gas price in dollars per MMBtu
        boiler_efficiency (float): Boiler efficiency as a decimal (0-1)
        lcfs_price_per_ton (float): LCFS credit price in dollars per ton CO₂e
        bau_emissions_factor (float): Business-as-usual emissions factor in tons CO₂e/MMBtu
        project_emissions_factor (float): Project emissions factor in tons CO₂e/MMBtu
        o_and_m_cost (float): Operations and maintenance cost in dollars per MMBtu
        return_components (bool): If True, returns a dictionary with all components

    Returns:
        float or dict: Net steam price ($/MMBtu) or dictionary with price components
    """

    # Step 1: Fuel cost per MMBtu of steam
    required_ng_per_mmbtu_steam = 1 / boiler_efficiency
    fuel_cost = ng_price_per_mmbtu * required_ng_per_mmbtu_steam

    # Step 2: Emissions avoided (tons CO₂e per MMBtu)
    emissions_avoided = bau_emissions_factor - project_emissions_factor

    # Step 3: LCFS credit per MMBtu
    lcfs_credit = emissions_avoided * lcfs_price_per_ton

    # Step 4: Final steam price
    net_steam_price = fuel_cost - lcfs_credit + o_and_m_cost
    
    if return_components:
        return {
            "net_steam_price": round(net_steam_price, 2),
            "fuel_cost": round(fuel_cost, 2),
            "lcfs_credit": round(lcfs_credit, 2),
            "emissions_avoided": emissions_avoided,
            "required_ng_per_mmbtu_steam": required_ng_per_mmbtu_steam
        }
    
    return round(net_steam_price, 2)

def perform_sensitivity_analysis(param_name, param_range, fixed_params):
    """
    Perform sensitivity analysis by varying one parameter while keeping others constant.
    
    Args:
        param_name (str): Name of the parameter to vary
        param_range (list or numpy array): Range of values for the parameter
        fixed_params (dict): Dictionary of all parameters with their fixed values
    
    Returns:
        pandas.DataFrame: DataFrame with parameter values and corresponding steam prices
    """
    results = []
    
    for value in param_range:
        # Create a copy of fixed parameters
        params = fixed_params.copy()
        
        # Update the parameter to vary
        params[param_name] = value
        
        # Calculate steam price with the updated parameter
        steam_price = calculate_steam_price(**params)
        
        # Store the result
        results.append({
            "param_value": value,
            "steam_price": steam_price
        })
    
    return pd.DataFrame(results)

def calculate_revenue_sharing(
    steam_price=5.00,
    baseline_steam_price=7.50,
    annual_steam_usage=100000,  # MMBtu
    lcfs_credit_value=50000,    # $ per year
    capital_investment=1000000,  # $
    project_lifetime=10,        # years
    discount_rate=0.08,         # 8%
    revenue_share_percentage=0.5,  # 50% of cost savings to the offtaker
    return_detailed=False
):
    """
    Calculate the revenue sharing between steam offtaker (industrial customer) and 
    producer (energy solutions provider) based on cost savings.
    
    Args:
        steam_price (float): Calculated steam price ($/MMBtu)
        baseline_steam_price (float): Current or business-as-usual steam price ($/MMBtu)
        annual_steam_usage (float): Annual steam consumption (MMBtu)
        lcfs_credit_value (float): Annual value of LCFS credits ($)
        capital_investment (float): Initial capital investment for the project ($)
        project_lifetime (int): Expected project lifetime in years
        discount_rate (float): Annual discount rate for NPV calculations (as decimal)
        revenue_share_percentage (float): Percentage of cost savings going to offtaker (as decimal)
        return_detailed (bool): If True, returns detailed NPV and cash flow information
    
    Returns:
        dict: Results of the revenue sharing analysis
    """
    # Calculate annual cost savings
    annual_cost_savings = (baseline_steam_price - steam_price) * annual_steam_usage
    
    # Calculate total annual benefit
    total_annual_benefit = annual_cost_savings + lcfs_credit_value
    
    # Calculate offtaker and producer shares
    offtaker_annual_share = annual_cost_savings * revenue_share_percentage
    producer_annual_share = total_annual_benefit - offtaker_annual_share
    
    # NPV calculations
    cash_flows = []
    producer_cash_flows = [-capital_investment]  # Initial investment (year 0)
    offtaker_cash_flows = [0]  # No initial investment for offtaker
    
    for year in range(1, project_lifetime + 1):
        producer_cf = producer_annual_share
        offtaker_cf = offtaker_annual_share
        
        # Discount to present value
        pv_factor = 1 / ((1 + discount_rate) ** year)
        producer_cash_flows.append(producer_cf)
        offtaker_cash_flows.append(offtaker_cf)
        
        cash_flows.append({
            "year": year,
            "producer_cash_flow": producer_cf,
            "offtaker_cash_flow": offtaker_cf,
            "producer_pv": producer_cf * pv_factor,
            "offtaker_pv": offtaker_cf * pv_factor
        })
    
    # Calculate NPVs
    producer_npv = npf.npv(discount_rate, producer_cash_flows)
    offtaker_npv = npf.npv(discount_rate, offtaker_cash_flows)
    
    # Calculate IRR for producer
    try:
        producer_irr = npf.irr(producer_cash_flows)
    except:
        producer_irr = None  # IRR may not exist in some cases
    
    # Payback period (simple)
    cumulative_producer_cf = np.cumsum(producer_cash_flows)
    payback_years = None
    for i, cf in enumerate(cumulative_producer_cf):
        if cf >= 0:
            # Interpolate for partial year
            if i > 0:
                prev_cf = cumulative_producer_cf[i-1]
                fraction = -prev_cf / (cf - prev_cf)
                payback_years = i - 1 + fraction
            else:
                payback_years = i
            break
    
    results = {
        "annual_cost_savings": round(annual_cost_savings, 2),
        "lcfs_credit_value": round(lcfs_credit_value, 2),
        "total_annual_benefit": round(total_annual_benefit, 2),
        "offtaker_annual_share": round(offtaker_annual_share, 2),
        "producer_annual_share": round(producer_annual_share, 2),
        "producer_npv": round(producer_npv, 2),
        "offtaker_npv": round(offtaker_npv, 2),
        "producer_irr": round(producer_irr * 100, 2) if producer_irr is not None else None,
        "payback_period": round(payback_years, 2) if payback_years is not None else None,
        "revenue_share_percentage": revenue_share_percentage * 100  # Convert to percentage
    }
    
    if return_detailed:
        results["cash_flows"] = cash_flows
    
    return results
