# Steam Price Calculator

This is an interactive Streamlit application for calculating steam prices based on various factors including natural gas costs, boiler efficiency, LCFS credits, and emissions.

## Features

- Interactive calculator for determining steam prices
- Input fields for all variables (natural gas price, boiler efficiency, LCFS price, emissions factors, O&M costs)
- Results display showing calculated steam price
- Visual representation of cost breakdown
- Sensitivity analysis for key parameters
- Detailed methodology explanation

## How to Run

1. Install the required dependencies:
   ```
   pip install streamlit pandas plotly numpy
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

## Calculation Methodology

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

## Parameters

- **Natural Gas Price**: The cost of natural gas per MMBtu (Million British Thermal Units)
- **Boiler Efficiency**: The thermal efficiency of the boiler (ratio of heat transferred to steam vs. fuel energy input)
- **LCFS Price**: The price of Low Carbon Fuel Standard credits per metric ton of CO₂ equivalent
- **Business-as-usual Emissions Factor**: Emissions factor in metric tons of CO₂ equivalent per MMBtu for the baseline case
- **Project Emissions Factor**: Emissions factor in metric tons of CO₂ equivalent per MMBtu for the project case
- **O&M Cost**: Operations and Maintenance costs per MMBtu of steam produced
