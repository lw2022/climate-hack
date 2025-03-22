import csv

def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        data = {rows[0]: float(rows[1]) for rows in reader}
    return data

def calculate_steam_price(
    ng_price_per_mmbtu,
    lcfs_price_per_ton,
    boiler_efficiency=0.85,
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

    # Step 4: Net steam price
    net_steam_price = fuel_cost - lcfs_credit + o_and_m_cost

    return net_steam_price

def main():
    # Read input data from CSV files
    ng_data = read_csv('ng_price.csv')
    lcfs_data = read_csv('lcfs_price.csv')

    # Extract the necessary values
    ng_price_per_mmbtu = ng_data['NG Price']
    lcfs_price_per_ton = lcfs_data['LCFS Price']

    # Calculate the steam price
    steam_price = calculate_steam_price(ng_price_per_mmbtu, lcfs_price_per_ton)

    print(f"The calculated steam price is: ${steam_price:.2f} per MMBtu")

if __name__ == "__main__":
    main()
