# ⚡ EU ETS Grid Carbon Analytics

### 💼 Business Use Case

**Forecasting Carbon Price Volatility via Physical Fundamentals**

This engine correlates **Physical Power Grid Data** (Generation by Coal, Gas, Wind) with **Financial Compliance Data** (EU ETS Verified Emissions vs. Free Allocations).

**Value Proposition:**

*   **For Traders:** Identifies "structural shorts" (deficits). If a country with a high carbon deficit increases Coal generation, demand for EUAs (Carbon Credits) rises, signaling a **bullish price movement**.

*   **For Analysts:** Validates if financial deficits are driven by structural grid constraints (e.g., Low Wind requiring High Coal) or temporary economic factors.

---

### 📊 Data Sources

The pipeline aggregates data from two official sources to create a unified view of the European Carbon Market:

1.  **Financial Compliance Data (EU ETS):**

    *   *Source:* [European Environment Agency (EEA) Data Hub](https://www.eea.europa.eu/en/datahub/datahubitem-view/98f04097-26de-4fca-86c4-63834818c0c0)

    *   *Metric:* Verified Emissions, Freely Allocated Allowances, Surrendered Units.

2.  **Physical Grid Data:**

    *   *Source:* [Ember Energy - Yearly Electricity Data](https://ember-energy.org/data/yearly-electricity-data/)

    *   *Metric:* TWh Generation by Fuel (Coal, Lignite, Gas, Nuclear, Renewables).

---

## 📊 Project Report

[Click here to open PDF](https://github.com/sameerhussai230/EU-ETS-Grid-Carbon-Analytics/blob/main/dashboard.pdf)


---

### 🚀 Key Features

*   **ETL Pipeline:** Extracts Excel data from EEA and enriches it with live API calls to Ember.

*   **Smart Join Logic:** Maps ISO3 Country Codes (API) to ETS Registry Names (Excel) to ensure accurate merging of disparate datasets.

*   **Deficit Calculation:** Automatically calculates `Net Carbon Position = Verified Emissions - Free Allowances`.

*   **Provisional Forecasting:** Generates 2024-2025 provisional data estimates based on EU Phase 4 reduction trends (if official registry data is delayed).

*   **Interactive Dashboard:** Streamlit app with Plotly visualizations to analyze "Top Buyers" and "Correlation Scatter Plots".

Here’s the same section rewritten cleanly and ready to **copy-paste directly into your GitHub README** 👇

---

## 🛠️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sameerhussai230/EU-ETS-Grid-Carbon-Analytics.git
cd EU-ETS-Grid-Carbon-Analytics
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Environment Variables

Create a `.env` file in the root directory and add your Ember API key:

```env
EMBER_API_KEY=your_api_key_here
```

---

## ▶️ Usage

### 1️⃣ Run the ETL Pipeline

Process raw Excel data and fetch the latest grid stats:

```bash
python main.py
```

### 2️⃣ Launch the Dashboard

Start the local analytics server:

```bash
streamlit run app.py
```



