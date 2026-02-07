import requests
import pandas as pd
import os
from dotenv import load_dotenv

class EmberAPIExtractor:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("EMBER_API_KEY")
        self.base_url = "https://api.ember-energy.org/v1/electricity-generation/yearly"
        
        if not self.api_key:
            raise ValueError("❌ Critical Error: EMBER_API_KEY is missing from .env file.")

    def get_eu_generation(self, start_year=2000):
        """
        Fetches generation data. Defaults to 2000 to cover full EU ETS history (starting 2005).
        """
        print(f"⚡ Connecting to Ember API (Physical Grid Data from {start_year})...")
        
        # ISO3 Codes for major EU economies + GB (History)
        target_countries = [
            "DEU", "FRA", "ITA", "POL", "ESP", "NLD", "BEL", "CZE", "AUT", 
            "SWE", "ROU", "IRL", "GRC", "PRT", "FIN", "DNK", "HUN", "SVK", 
            "BGR", "HRV", "EST", "LVA", "LTU", "SVN", "LUX", "CYP", "MLT", "GBR"
        ]
        
        country_param = ",".join(target_countries)

        params = {
            "api_key": self.api_key,
            "entity_code": country_param,     
            "start_date": start_year,         
            "is_aggregate_series": "false"
        }

        try:
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return pd.DataFrame()
                
            data = response.json()
            if 'data' not in data:
                return pd.DataFrame()

            raw_df = pd.DataFrame(data['data'])
            return self._transform(raw_df)

        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return pd.DataFrame()

    def _transform(self, df):
        if df.empty:
            return df
            
        df['year'] = pd.to_datetime(df['date']).dt.year
        
        # We need these specifically to correlate with carbon pricing/deficit
        target_fuels = ['Coal', 'Gas', 'Wind', 'Solar', 'Nuclear', 'Hydro']
        df = df[df['series'].isin(target_fuels)]

        pivot_df = df.pivot_table(
            index=['entity_code', 'year'],
            columns='series',
            values='generation_twh',
            aggfunc='sum'
        ).reset_index()

        pivot_df.columns.name = None
        pivot_df = pivot_df.fillna(0)
        return pivot_df