import pandas as pd
import os

# --- CONFIGURATION ---
OUTPUT_FILE = "output/eu_market_analysis_final.csv"

def perform_output_eda():
    print(f"🔎 STARTING POST-ETL AUDIT on: {OUTPUT_FILE}\n")
    
    if not os.path.exists(OUTPUT_FILE):
        print(f"❌ CRITICAL: File not found. Run 'main.py' first.")
        return

    # 1. Load Data
    try:
        df = pd.read_csv(OUTPUT_FILE)
        print("✅ File Loaded Successfully.")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # 2. Structure Check
    print(f"\n--- 1. STRUCTURE & COLUMNS ---")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {list(df.columns)}")
    
    # Check if API columns exist
    api_cols = ['Coal', 'Wind', 'Solar', 'Gas']
    found_api = [c for c in api_cols if c in df.columns]
    if found_api:
        print(f"✅ API Columns Found: {found_api}")
    else:
        print(f"⚠️ WARNING: No Energy API columns found. Merge might have failed.")

    # 3. Sector Name Verification (Did Regex work?)
    print(f"\n--- 2. SECTOR CLEANLINESS CHECK ---")
    sectors = df['main_activity_sector_name'].unique()
    print("Sample Sectors (Should NOT see '20-99' or '10'):")
    print(sorted(sectors)[:5])
    
    # Validation logic
    dirty_sectors = [s for s in sectors if s[0].isdigit()]
    if dirty_sectors:
        print(f"❌ FAILED: Found dirty sector names: {dirty_sectors}")
    else:
        print("✅ SUCCESS: All sector names appear clean.")

    # 4. Merge Quality Check (Did 'Germany' get Coal data?)
    print(f"\n--- 3. DATA MERGE VALIDATION (Example: Germany) ---")
    # Filter for a major country that definitely has Ember data
    de_data = df[df['country'] == 'Germany']
    if not de_data.empty:
        # Check if Coal is present and not 0/NaN for a recent year
        recent_de = de_data.sort_values(by='year', ascending=False).iloc[0]
        print(f"Sample Row (Germany, {recent_de['year']}):")
        print(f"   Sector: {recent_de['main_activity_sector_name']}")
        print(f"   Deficit: {recent_de['carbon_deficit']:,.0f}")
        
        if 'Coal' in recent_de:
            print(f"   Coal Gen: {recent_de['Coal']} TWh")
            if pd.isna(recent_de['Coal']):
                 print("   ❌ Coal is NaN (Merge Failed)")
            elif recent_de['Coal'] == 0:
                 print("   ⚠️ Coal is 0 (Data might be missing in API or Year mismatch)")
            else:
                 print("   ✅ Coal data verified.")
        else:
             print("   ❌ Coal column missing.")
    else:
        print("⚠️ Germany not found in dataset (Check ISO mapping).")

    # 5. Year & Forecast Check
    print(f"\n--- 4. YEAR RANGE CHECK ---")
    years = sorted(df['year'].unique())
    print(f"Years present: {years}")
    
    if 2024 in years or 2025 in years:
        print("✅ Provisional Forecast Data DETECTED.")
    else:
        print("ℹ️ Standard Data Only (No Forecast generated).")

    # 6. Unit Magnitude Check (Are we in Tons or Millions?)
    print(f"\n--- 5. UNIT MAGNITUDE CHECK ---")
    max_val = df['carbon_deficit'].max()
    print(f"Max Deficit Value: {max_val:,.0f}")
    
    if max_val > 1_000_000:
        print("✅ Units appear to be absolute TONS (Correct for ETS).")
    else:
        print("⚠️ Units look small. Check if source was in Millions.")

    print("\n✅ Post-ETL Audit Complete.")

if __name__ == "__main__":
    perform_output_eda()