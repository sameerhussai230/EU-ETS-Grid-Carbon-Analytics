import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="EU Carbon Desk",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---
def format_large_number(num):
    """
    Formats large numbers into human-readable strings (B, M, k).
    Examples:
        1,500,000 -> 1.5 M
        573,172,582 -> 573.2 M
        -25,000 -> -25.0 k
    """
    if pd.isna(num):
        return "0"
    
    magnitude = 0
    abs_num = abs(num)
    
    while abs_num >= 1000:
        magnitude += 1
        abs_num /= 1000.0
        
    # Choose suffix
    suffix = ['', 'k', 'M', 'B', 'T'][magnitude]
    
    # Format: 1 decimal place if M/B, otherwise 0
    if magnitude >= 2: # Millions or Billions
        return f'{num / (1000**magnitude):.1f} {suffix}'
    elif magnitude == 1: # Thousands
        return f'{num / (1000**magnitude):.0f} {suffix}'
    else:
        return f'{num:.0f}'

def safe_sum(dataframe, col_name):
    return dataframe[col_name].sum() if col_name in dataframe.columns else 0

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = "output/eu_market_analysis_final.csv"
    # Check if file exists to prevent crash on fresh pull
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

import os # Ensure os is imported for file check
df = load_data()

if df.empty:
    st.error("🚨 No Data Found. Please run 'main.py' to generate the report.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🔎 Market Scanner")

# 1. Year Selection
if 'year' in df.columns:
    years = sorted(df['year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Analysis Year", years, index=0)
else:
    st.error("Data missing 'year' column.")
    st.stop()

# 2. Sector Selection
if 'main_activity_sector_name' in df.columns:
    sectors = sorted(df['main_activity_sector_name'].unique())
    # Default to Combustion if available
    default_sec = "Combustion of fuels"
    if default_sec not in sectors:
        default_sec = sectors[0]
        
    idx = sectors.index(default_sec) if default_sec in sectors else 0
    selected_sector = st.sidebar.selectbox("Sector", sectors, index=idx)
else:
    st.error("Data missing 'main_activity_sector_name' column.")
    st.stop()

# --- FILTERING ---
df_filtered = df[(df['year'] == selected_year) & (df['main_activity_sector_name'] == selected_sector)].copy()

# Filter out aggregates found in EDS (Double safety, though ETL handles this)
aggregates = [
    'All Countries', 'EU27', 'EU27 + UK', 
    'Recovery and Resilience Facility', 'United Kingdom (excl. NI)'
]

if 'country' in df_filtered.columns:
    df_countries = df_filtered[~df_filtered['country'].isin(aggregates)].copy()
else:
    df_countries = df_filtered.copy()

# --- DASHBOARD HEADER ---
st.title(f"⚡ EU Carbon Market Analysis ({selected_year})")

if selected_year >= 2024:
    st.info(f"ℹ️ NOTE: Data for {selected_year} includes PROVISIONAL estimates based on EU Phase 4 reduction schedules.")

# --- KPIs ---
total_deficit = safe_sum(df_countries, 'carbon_deficit')
total_coal = safe_sum(df_countries, 'Coal')

col1, col2, col3 = st.columns(3)

# Logic for Delta Colors
if total_deficit > 0:
    delta_text = "Market Shortage (Buy)"
    delta_color = "inverse" # Red in Streamlit
else:
    delta_text = "Market Surplus (Sell)"
    delta_color = "normal"  # Green in Streamlit

# Formatting Values using the new function
formatted_deficit = format_large_number(total_deficit)
formatted_coal = format_large_number(total_coal)

col1.metric(
    "Net Carbon Position", 
    f"{formatted_deficit} tCO2", 
    delta=delta_text, 
    delta_color=delta_color
)

col2.metric(
    "Total Coal Gen (Grid)", 
    f"{formatted_coal} TWh", 
    delta="Physical Load"
)

col3.metric("Selected Sector", selected_sector)

st.divider()

# --- CHARTS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader(f"🏆 Top Deficits: {selected_sector}")
    
    if not df_countries.empty and 'carbon_deficit' in df_countries.columns:
        # Show top 10 buyers (Deficit > 0)
        top_deficits = df_countries.sort_values(by='carbon_deficit', ascending=False).head(10)
        
        fig_bar = px.bar(
            top_deficits, 
            x='country', 
            y='carbon_deficit', 
            color='carbon_deficit', 
            color_continuous_scale='Reds',
            title="Largest Buyers of EUAs (Carbon Credits)",
            labels={'carbon_deficit': 'Deficit (tCO2)', 'country': 'Country'}
        )
        # Update bar chart layout for readability
        fig_bar.update_layout(xaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No data available for charts.")

with c2:
    st.subheader("🔗 Correlation Engine")
    st.caption("Macro Analysis: Correlating Grid Carbon Intensity (Coal) with Sector Financials.")
    
    required_cols = ['Coal', 'carbon_deficit', 'verified_emissions']
    if all(col in df_countries.columns for col in required_cols):
        # Filter for meaningful visualization (remove 0 coal if checking correlation)
        df_chart = df_countries.dropna(subset=['Coal', 'carbon_deficit'])
        
        if not df_chart.empty:
            fig_scatter = px.scatter(
                df_chart, 
                x='Coal', 
                y='carbon_deficit', 
                size='verified_emissions', 
                color='country', 
                title=f"Correlation: Grid Coal Power vs. {selected_sector} Deficit",
                labels={
                    'Coal': 'Grid Coal Generation (TWh)', 
                    'carbon_deficit': 'Sector Carbon Deficit',
                    'verified_emissions': 'Emission Volume'
                },
                trendline="ols" if len(df_chart) > 2 else None # Only trendline if enough points
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning(f"Insufficient overlap between Physical Grid Data and {selected_sector} Financials.")
    else:
        st.info("Physical grid data not available for this view.")

# --- DATA TABLE ---
with st.expander("📄 View Detailed Ledger", expanded=True):
    potential_cols = ['year', 'country', 'carbon_deficit', 'verified_emissions', 'allocated_allowances', 'Coal', 'Wind']
    display_cols = [c for c in potential_cols if c in df_countries.columns]
    
    # Secure Formatting: prevent crashes on text columns
    numeric_cols = ['carbon_deficit', 'verified_emissions', 'allocated_allowances', 'Coal', 'Wind']
    format_dict = {col: "{:,.0f}" for col in numeric_cols if col in df_countries.columns}

    if not df_countries.empty:
        st.dataframe(
            df_countries[display_cols]
            .sort_values(by='carbon_deficit', ascending=False)
            .style.format(format_dict)
        )
    else:
        st.write("No data to display.")