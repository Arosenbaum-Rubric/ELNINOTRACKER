import pandas as pd
RAW = r"C:\Users\arosenbaum\Downloads\ELNINO tracker\data\raw\Palm Oil data"
psd = pd.read_csv(RAW + r"\psd_oilseeds.csv", dtype={"Commodity_Code": str})
prod = psd[(psd["Commodity_Code"]=="4243000") & (psd["Attribute_ID"]==28) & (psd["Market_Year"].between(2005,2026))].copy()
prod = prod.sort_values(["Market_Year","Country_Code","Calendar_Year","Month"])
latest = prod.groupby(["Market_Year","Country_Code"]).last().reset_index()
global_tot = latest.groupby("Market_Year")["Value"].sum().reset_index()
global_tot["mmt"] = (global_tot["Value"] / 1000).round(1)
for _, r in global_tot.iterrows():
    print(f"  {{yr:{int(r.Market_Year)}, mmt:{r.mmt}}},")
