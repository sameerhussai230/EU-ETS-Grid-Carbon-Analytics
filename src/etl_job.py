import pandas as pd
import os
import re
from src.extractors.ember_api import EmberAPIExtractor

class EU_ETS_Transformer:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        
        # Define aggregates found in EDS to remove from final dataset
        self.aggregates_to_drop = [
            'All Countries', 'EU27', 'EU27 + UK', 
            'Recovery and Resilience Facility', 'Northern Ireland',
            'EU25', 'EU28'
        ]

    def extract(self):
        print(f"⏳ Reading Excel file: {self.input_path} (Please wait...)")
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"❌ File not found at {self.input_path}")

        df = pd.read_excel(self.input_path)
        # Standardize columns
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        return df

    def transform(self, df):
        print("⚙️  Transforming Compliance Data...")

        # 1. Clean Year
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        df = df.dropna(subset=['year']).copy()
        df['year'] = df['year'].astype(int)

        # 2. Filter Aggregates (NEW STEP: Clean data at source)
        df = df[~df['country'].isin(self.aggregates_to_drop)]

        # 3. Drop rows with missing 'value'
        df = df.dropna(subset=['value'])

        # 4. Filter Metrics
        relevant_metrics = [
            "1. Total allocated allowances (EUA or EUAA)",
            "2. Verified emissions"
        ]
        df_filtered = df[df['ets_information'].isin(relevant_metrics)].copy()

        # 5. Clean Sector Names (Regex confirmed working by EDS)
        df_filtered['main_activity_sector_name'] = df_filtered['main_activity_sector_name'].astype(str).str.replace(r'^[\d-]+\s+', '', regex=True)

        # 6. Pivot
        pivot_df = df_filtered.pivot_table(
            index=['year', 'country', 'main_activity_sector_name'],
            columns='ets_information',
            values='value',
            aggfunc='sum'
        ).reset_index()

        pivot_df.columns.name = None
        pivot_df = pivot_df.rename(columns={
            "1. Total allocated allowances (EUA or EUAA)": "allocated_allowances",
            "2. Verified emissions": "verified_emissions"
        })

        # 7. Smart Forecasting
        max_year = pivot_df['year'].max()
        if max_year < 2025: 
            print(f"🔮 Generating Provisional Data for {max_year + 1} based on EU Trends...")
            provisional_df = self.generate_provisional_next_year(pivot_df, max_year)
            pivot_df = pd.concat([pivot_df, provisional_df], ignore_index=True)

        # 8. Calculate Deficit
        pivot_df['allocated_allowances'] = pivot_df['allocated_allowances'].fillna(0)
        pivot_df['verified_emissions'] = pivot_df['verified_emissions'].fillna(0)
        pivot_df['carbon_deficit'] = pivot_df['verified_emissions'] - pivot_df['allocated_allowances']

        return pivot_df

    def generate_provisional_next_year(self, df, base_year):
        base_df = df[df['year'] == base_year].copy()
        base_df['year'] = base_year + 1

        # Aviation: +5% Activity, -25% Free Allowances
        aviation_mask = base_df['main_activity_sector_name'].str.contains("Aviation", case=False, na=False)
        base_df.loc[aviation_mask, 'verified_emissions'] *= 1.05
        base_df.loc[aviation_mask, 'allocated_allowances'] *= 0.75 

        # Power: -15% Emissions
        power_mask = base_df['main_activity_sector_name'].str.contains("Combustion", case=False, na=False)
        base_df.loc[power_mask, 'verified_emissions'] *= 0.85
        
        return base_df

    def enrich_with_api_data(self, compliance_df):
        # UPDATED: Start from 2005 to match ETS history for correlation
        print("\n🔗 Enriching Financials with Physical Grid Data (Ember API)...")
        ember = EmberAPIExtractor()
        phy_df = ember.get_eu_generation(start_year=2005)
        
        if phy_df.empty:
            return compliance_df

        # Complete ISO Mapper based on EDS Country list
        iso_mapper = {
            'DEU': 'Germany', 'FRA': 'France', 'ITA': 'Italy', 
            'POL': 'Poland', 'ESP': 'Spain', 'NLD': 'Netherlands', 
            'BEL': 'Belgium', 'CZE': 'Czechia', 'AUT': 'Austria', 
            'SWE': 'Sweden', 'ROU': 'Romania', 'IRL': 'Ireland', 
            'GRC': 'Greece', 'PRT': 'Portugal', 'FIN': 'Finland', 
            'DNK': 'Denmark', 'HUN': 'Hungary', 'SVK': 'Slovakia', 
            'BGR': 'Bulgaria', 'HRV': 'Croatia', 'EST': 'Estonia',
            'LVA': 'Latvia', 'LTU': 'Lithuania', 'SVN': 'Slovenia',
            'LUX': 'Luxembourg', 'CYP': 'Cyprus', 'MLT': 'Malta',
            'GBR': 'United Kingdom (excl. NI)' # Specific map for Brexit context
        }
        
        phy_df['country_mapped'] = phy_df['entity_code'].map(iso_mapper)
        
        # Merge
        merged_df = pd.merge(
            compliance_df,
            phy_df,
            left_on=['country', 'year'],
            right_on=['country_mapped', 'year'],
            how='left'
        )
        
        merged_df = merged_df.drop(columns=['country_mapped', 'entity_code'])
        return merged_df

    def load(self, df):
        print(f"💾 Saving final report to {self.output_path}...")
        df.to_csv(self.output_path, index=False)
        print("✅ ETL Pipeline Finished Successfully.")