from src.etl_job import EU_ETS_Transformer
import os

def main():
    # 1. Configuration
    INPUT_FILE = "data/ETS_DataViewer_20250916.xlsx"
    OUTPUT_FILE = "output/eu_market_analysis_final.csv"

    # 2. Check Input
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file not found at {INPUT_FILE}")
        return

    # 3. Initialize Pipeline
    etl = EU_ETS_Transformer(INPUT_FILE, OUTPUT_FILE)

    try:
        raw_data = etl.extract()
        clean_data = etl.transform(raw_data)
        final_data = etl.enrich_with_api_data(clean_data)
        etl.load(final_data)

    except Exception as e:
        print(f"\n❌ Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()