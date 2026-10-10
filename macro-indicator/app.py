from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT=Path(__file__).resolve().parent
PATH=ROOT/"data"/"observations.csv"
LABELS={"india_cpi_yoy":"India CPI inflation (YoY)","india_wpi_yoy":"India WPI inflation (YoY)","us_fed_funds":"US Effective Federal Funds Rate","us_cpi_yoy":"US CPI inflation (YoY)","rbi_repo":"RBI Repo Rate","rbi_reverse_repo":"RBI Reverse Repo Rate"}
st.set_page_config(page_title="Macro Indicator Dashboard",layout="wide")
st.title("Macro Economic Indicators Dashboard")
st.caption("Official-source observations • independent date ranges • editable research remarks")
df=pd.read_csv(PATH) if PATH.exists() else pd.DataFrame(columns=["indicator","country","period_date","release_date","value","unit","source_url","source_name","remarks"])
if not df.empty:
    df["period_date"]=pd.to_datetime(df["period_date"],errors="coerce")
    df["value"]=pd.to_numeric(df["value"],errors="coerce")
    df=df.dropna(subset=["period_date","value"])
with st.sidebar:
    st.header("Analysis controls")
    available=list(LABELS)
    if not df.empty: available=sorted(set(available)|set(df.indicator))
    chosen=st.multiselect("Indicators",available,default=available)
    cfg={}
    for key in chosen:
        st.markdown("**"+LABELS.get(key,key)+"**")
        mode=st.selectbox("Range",["1Y","3Y","5Y","10Y","20Y","All","Custom"],index=3,key="mode_"+key)
        if mode=="Custom":
            a,b=st.columns(2)
            start=a.date_input("From",date.today()-timedelta(days=365),key="from_"+key)
            end=b.date_input("To",date.today(),key="to_"+key)
        elif mode=="All": start,end=date(1900,1,1),date.today()
        else: start,end=date.today()-timedelta(days=365*int(mode[:-1])),date.today()
        cfg[key]=(pd.Timestamp(start),pd.Timestamp(end))
    chart=st.radio("Chart type",["Column","Line","Area"],horizontal=True)
    labels=st.checkbox("Show value labels",True)

cards=st.columns(5)
for i,key in enumerate(LABELS):
    with cards[i]:
        sub=df[df.indicator==key] if not df.empty else df
        if not sub.empty:
            last=sub.sort_values("period_date").iloc[-1]
            st.metric(LABELS[key],f'{last["value"]:.2f} {last.get("unit","%")}',help=str(last["period_date"].date()))
        else: st.metric(LABELS[key],"No data")
st.subheader("Historical charts")
chartcols=st.columns(2)
for i,key in enumerate(chosen):
    if df.empty: continue
    sub=df[df.indicator==key].copy()
    if sub.empty: continue
    start,end=cfg[key]
    sub=sub[(sub.period_date>=start)&(sub.period_date<=end)].sort_values("period_date")
    if sub.empty:
        st.warning(f"No data in selected range: {LABELS.get(key,key)}")
        continue
    if chart=="Column": fig=px.bar(sub,x="period_date",y="value",title=LABELS.get(key,key),text="value" if labels else None)
    elif chart=="Line": fig=px.line(sub,x="period_date",y="value",title=LABELS.get(key,key),markers=True)
    else: fig=px.area(sub,x="period_date",y="value",title=LABELS.get(key,key))
    fig.update_layout(height=330,margin=dict(l=10,r=10,t=45,b=10),xaxis_title=None,yaxis_title=sub.iloc[-1].get("unit","Value"))
    with chartcols[i%2]: st.plotly_chart(fig,use_container_width=True)
st.subheader("History and remarks")
if not df.empty:
    view=df[df.indicator.isin(chosen)].copy()
    view["indicator_label"]=view.indicator.map(LABELS).fillna(view.indicator)
    if "remarks" not in view: view["remarks"]=""
    edited=st.data_editor(view[["period_date","indicator_label","country","value","unit","release_date","source_name","source_url","remarks"]],hide_index=True,use_container_width=True,
      column_config={"period_date":st.column_config.DateColumn("Period",disabled=True),"indicator_label":st.column_config.TextColumn("Indicator",disabled=True),"country":st.column_config.TextColumn("Country",disabled=True),"value":st.column_config.NumberColumn("Value",disabled=True),"unit":st.column_config.TextColumn("Unit",disabled=True),"release_date":st.column_config.TextColumn("Release date",disabled=True),"source_name":st.column_config.TextColumn("Source",disabled=True),"source_url":st.column_config.LinkColumn("Source link",disabled=True),"remarks":st.column_config.TextColumn("Remarks (editable)",width="large")})
    st.download_button("Download remarks CSV",edited[["indicator_label","period_date","remarks"]].to_csv(index=False).encode(),"remarks.csv","text/csv")
    st.download_button("Download filtered observations CSV",view.to_csv(index=False).encode(),"macro_observations.csv","text/csv")
else: st.info("No observations yet. Configure FRED_API_KEY for US series, then add verified India observations.")
with st.expander("How to add verified India observations"):
    st.markdown("Add rows to `data/observations.csv` with columns: `indicator,country,period_date,release_date,value,unit,source_url,source_name,remarks`. Keys: `india_cpi_yoy`, `india_wpi_yoy`, `rbi_repo`, `rbi_reverse_repo`. Use official sources and numeric percentages. The dashboard never fabricates missing values.")
