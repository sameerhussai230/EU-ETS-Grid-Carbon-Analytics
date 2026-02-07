import pandas as pd
import os

# --- CONFIGURATION ---
INPUT_FILE = "data/ETS_DataViewer_20250916.xlsx"

def perform_eds():
    print(f"🔍 STARTING EDS (Exploratory Data Scanning) on: {INPUT_FILE}\n")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ CRITICAL: File not found at {INPUT_FILE}")
        return

    # 1. Load Data
    try:
        # Load header to see raw names first
        df_raw = pd.read_excel(INPUT_FILE, nrows=5)
        print("--- 1. RAW COLUMN HEADERS (As they appear in Excel) ---")
        print(list(df_raw.columns))
        print("\n")
        
        # Load full dataset
        print("⏳ Loading full dataset... (This may take a moment)")
        df = pd.read_excel(INPUT_FILE)
        
        # Standardize columns (Mocking ETL logic to see if it works)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        print("✅ Columns Normalized to Snake Case:")
        print(list(df.columns))
        print("-" * 50)

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # 2. General Overview
    print(f"\n--- 2. DATASET SHAPE ---")
    print(f"Rows: {df.shape[0]:,}")
    print(f"Columns: {df.shape[1]}")
    
    # 3. Missing Values Audit
    print(f"\n--- 3. MISSING VALUES CHECK ---")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✅ No missing values found in any column.")
    else:
        print(missing[missing > 0])

    # 4. Numeric Column Analysis (Range & Stats)
    print(f"\n--- 4. NUMERIC COLUMN STATS ---")
    # Force conversion of 'value' to numeric to check for non-number garbage
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        print(f"\n🔹 Column: [{col}]")
        print(f"   Min: {df[col].min():,.2f}")
        print(f"   Max: {df[col].max():,.2f}")
        print(f"   Mean: {df[col].mean():,.2f}")
        if col == 'year':
            print(f"   Unique Years: {sorted(df[col].unique())}")

    # 5. Categorical Analysis (Unique Values)
    print(f"\n--- 5. CATEGORICAL COLUMN ANALYSIS ---")
    # Focus on specific columns important for the project
    
    target_cats = ['main_activity_sector_name', 'ets_information', 'country', 'unit']
    
    for col in target_cats:
        if col in df.columns:
            print(f"\n🔶 Column: [{col}]")
            unique_vals = df[col].astype(str).unique()
            count = len(unique_vals)
            
            print(f"   Total Unique Values: {count}")
            
            if count < 50:
                # If few values, print them all (Vertical list for readability)
                print(f"   Values: {sorted(unique_vals)}")
            else:
                # If many values, print top 10 and bottom 10
                print(f"   Too many to list. Showing sample:")
                print(f"   First 5: {sorted(unique_vals)[:5]}")
                print(f"   Last 5:  {sorted(unique_vals)[-5:]}")
                
                # SPECIAL CHECK: Check for 'Aviation' and 'Combustion' specifically
                if 'sector' in col:
                    has_aviation = any("aviation" in x.lower() for x in unique_vals)
                    has_combustion = any("combustion" in x.lower() for x in unique_vals)
                    print(f"   🔍 Check: Contains 'Aviation'? {'✅ Yes' if has_aviation else '❌ No'}")
                    print(f"   🔍 Check: Contains 'Combustion'? {'✅ Yes' if has_combustion else '❌ No'}")

        else:
            print(f"⚠️ Warning: Column '{col}' not found in dataset.")

    # 6. Specific Metric Validation
    print(f"\n--- 6. PROJECT CRITICAL CHECKS ---")
    if 'ets_information' in df.columns:
        ets_types = df['ets_information'].unique()
        print("Checking for required metrics in 'ets_information':")
        
        req_metrics = [
            "1. Total allocated allowances (EUA or EUAA)",
            "2. Verified emissions"
        ]
        
        for req in req_metrics:
            if req in ets_types:
                print(f"   ✅ Found: '{req}'")
            else:
                print(f"   ❌ MISSING: '{req}' (ETL will fail! Check spelling below)")
                print(f"      Available options: {ets_types}")

    print("\n✅ EDS Complete.")

if __name__ == "__main__":
    perform_eds()