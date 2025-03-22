def calculate_steam_price(
    ng_price_per_mmbtu=4.00,
    boiler_efficiency=0.85,
    lcfs_price_per_ton=100,
    bau_emissions_factor=0.053,    # in metric tons CO₂e per MMBtu
    project_emissions_factor=0.0053,
    o_and_m_cost=0.50
):
    """
    Calculate steam price ($/MMBtu) based on:
    - Natural gas cost
    - Boiler efficiency
    - LCFS carbon credit based on avoided CO₂e emissions
    - Optional O&M costs

    Returns: Net steam price ($/MMBtu)
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
    print(f"The calculated steam price is: ${net_steam_price:.2f} per MMBtu")

    return round(net_steam_price, 2)
