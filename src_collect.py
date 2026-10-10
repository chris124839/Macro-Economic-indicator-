import os
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent
OBS_PATH = ROOT / "data" / "observations.csv"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"
COLS = ["indicator","country","period_date","release_date","value","unit","source_url","source_name","remarks"]

def fetch_fred(series_id, indicator, country, unit, transform=None):
    key = os.getenv("FRED_API_KEY")
    if not key:
        print(f"Skip {series_id}: configure FRED_API_KEY.")
        return []
    r = requests.get(FRED_API, params={"series_id":series_id,"api_key":key,"file_type":"json","sort_order":"asc"}, timeout=30)
    r.raise_for_status()
    vals = [(x["date"],float(x["value"])) for x in r.json().get("observations",[]) if x.get("value") not in ("", ".", None)]
    rows=[]
    for i,(dt,val) in enumerate(vals):
        value = transform(vals,i) if transform else val
        if value is None: continue
        rows.append({"indicator":indicator,"country":country,"period_date":dt,"release_date":"","value":round(float(value),6),"unit":unit,
          "source_url":f"https://fred.stlouisfed.org/series/{series_id}","source_name":"FRED","remarks":""})
    return rows

def yoy(vals,i):
    if i < 12: return None
    return (vals[i][1]/vals[i-12][1]-1)*100

def main():
    old = pd.read_csv(OBS_PATH) if OBS_PATH.exists() else pd.DataFrame(columns=COLS)
    new = fetch_fred("FEDFUNDS","us_fed_funds","United States","%")
    new += fetch_fred("CPIAUCSL","us_cpi_yoy","United States","% YoY",yoy)
    if not new:
        print("No FRED observations fetched; retained existing data.")
        return
    combined = pd.concat([old,pd.DataFrame(new)],ignore_index=True)
    combined["value"] = pd.to_numeric(combined["value"],errors="coerce")
    combined = combined.dropna(subset=["value"]).drop_duplicates(["indicator","period_date"],keep="last")
    combined = combined.sort_values(["indicator","period_date"])
    combined.to_csv(OBS_PATH,index=False)
    print(f"Stored {len(combined)} observations.")
if __name__ == "__main__": main()
