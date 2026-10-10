from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "data" / "source"
OUT = ROOT / "data" / "observations.csv"
COLS = ["indicator","country","period_date","release_date","value","unit","source_url","source_name","remarks"]

# Adjust these aliases to match the headings in the files already committed to your repo.
ALIASES = {
    "indicator": ["indicator","series","series name","macro indicator","parameter","index"],
    "period_date": ["period_date","period","date","month","observation date","effective date","reference period"],
    "release_date": ["release_date","release date","published date","publication date"],
    "value": ["value","actual","rate","index value","inflation","percentage","percent","%"],
    "source_url": ["source_url","url","source link","link"],
    "source_name": ["source_name","source","publisher","agency"],
    "remarks": ["remarks","remark","notes","comment"],
}
INDICATOR_MAP = {
    "cpi":"india_cpi_yoy", "consumer price index":"india_cpi_yoy", "india cpi":"india_cpi_yoy",
    "cpi inflation":"india_cpi_yoy", "cpi yoy":"india_cpi_yoy", "india_cpi_yoy":"india_cpi_yoy",
    "wpi":"india_wpi_yoy", "wholesale price index":"india_wpi_yoy", "india wpi":"india_wpi_yoy",
    "wpi inflation":"india_wpi_yoy", "wpi yoy":"india_wpi_yoy", "india_wpi_yoy":"india_wpi_yoy",
    "repo":"rbi_repo", "repo rate":"rbi_repo", "policy repo rate":"rbi_repo", "rbi repo rate":"rbi_repo", "rbi_repo":"rbi_repo",
    "reverse repo":"rbi_reverse_repo", "reverse repo rate":"rbi_reverse_repo", "fixed reverse repo rate":"rbi_reverse_repo", "rbi_reverse_repo":"rbi_reverse_repo",
    "sdf":"rbi_sdf", "sdf rate":"rbi_sdf", "standing deposit facility rate":"rbi_sdf", "rbi_sdf":"rbi_sdf",
}
UNITS = {"india_cpi_yoy":"% YoY","india_wpi_yoy":"% YoY","rbi_repo":"%","rbi_reverse_repo":"%","rbi_sdf":"%"}

def norm(s):
    return re.sub(r"\s+"," ",str(s).strip().lower().replace("_"," "))

def find_col(df, logical):
    wanted = {norm(x) for x in ALIASES[logical]}
    for c in df.columns:
        if norm(c) in wanted: return c
    return None

def indicator_key(value, filename):
    raw = norm(value) if value is not None else ""
    for k,v in INDICATOR_MAP.items():
        if raw == norm(k): return v
    # Infer only from file name when clearly named; do not guess from arbitrary values.
    name = norm(filename)
    for k,v in INDICATOR_MAP.items():
        if k in name and len(k) > 2: return v
    return None

def read_file(path):
    try:
        if path.suffix.lower()==".csv": return [pd.read_csv(path)]
        if path.suffix.lower() in (".xlsx",".xls"): return list(pd.read_excel(path,sheet_name=None).values())
    except Exception as e:
        print(f"Could not read {path.name}: {e}")
    return []

def main():
    existing = pd.read_csv(OUT) if OUT.exists() else pd.DataFrame(columns=COLS)
    rows=[]
    if SOURCE_DIR.exists():
        for path in SOURCE_DIR.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in (".csv",".xlsx",".xls"): continue
            for df in read_file(path):
                if df.empty: continue
                date_col=find_col(df,"period_date")
                value_col=find_col(df,"value")
                indicator_col=find_col(df,"indicator")
                if not date_col or not value_col:
                    print(f"Skipping {path.name}: couldn't identify date/value columns.")
                    continue
                for _,r in df.iterrows():
                    key=indicator_key(r[indicator_col] if indicator_col else None,path.name)
                    if not key: continue
                    period=pd.to_datetime(r[date_col],errors="coerce",dayfirst=True)
                    val=pd.to_numeric(str(r[value_col]).replace("%","").replace(",",""),errors="coerce")
                    if pd.isna(period) or pd.isna(val): continue
                    def get(logical, default=""):
                        c=find_col(df,logical)
                        return str(r[c]) if c and pd.notna(r[c]) else default
                    rows.append({
                        "indicator":key,"country":"India","period_date":period.strftime("%Y-%m-%d"),
                        "release_date":get("release_date"),"value":float(val),
                        "unit":UNITS[key],"source_url":get("source_url"),
                        "source_name":get("source_name",path.stem),"remarks":get("remarks")
                    })
    if rows:
        merged=pd.concat([existing,pd.DataFrame(rows)],ignore_index=True)
        merged["value"]=pd.to_numeric(merged["value"],errors="coerce")
        merged=merged.dropna(subset=["value","period_date"])
        merged=merged.drop_duplicates(["indicator","period_date"],keep="last")
        merged=merged.sort_values(["indicator","period_date"])
        merged.to_csv(OUT,index=False)
        print(f"Processed {len(rows)} source rows; stored {len(merged)} observations.")
    else:
        print("No matching India observations found in data/source. Existing observations retained.")

if __name__=="__main__": main()
