from pathlib import Path
from datetime import date,timedelta
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT=Path(__file__).resolve().parent
PATH=ROOT/"data"/"observations.csv"
LABELS={"india_cpi_yoy":"India CPI Inflation (YoY)","india_wpi_yoy":"India WPI Inflation (YoY)","rbi_repo":"RBI Repo Rate","rbi_reverse_repo":"RBI Fixed Reverse Repo Rate","rbi_sdf":"RBI Standing Deposit Facility Rate"}
st.set_page_config(page_title="India Macro Dashboard",layout="wide")
st.title("India Macro Economic Indicators Dashboard")
st.caption("India-only • adjustable history per indicator • source-aware data and editable remarks")
df=pd.read_csv(PATH) if PATH.exists() else pd.DataFrame(columns=["indicator","country","period_date","release_date","value","unit","source_url","source_name","remarks"])
if not df.empty:
    df["period_date"]=pd.to_datetime(df["period_date"],errors="coerce")
    df["value"]=pd.to_numeric(df["value"],errors="coerce")
    df=df.dropna(subset=["period_date","value"])
with st.sidebar:
    st.header("Analysis controls")
    chosen=st.multiselect("Indicators",list(LABELS),default=list(LABELS),format_func=lambda x:LABELS[x])
    cfg={}
    for key in chosen:
        st.markdown("**"+LABELS[key]+"**")
        mode=st.selectbox("Date range",["1Y","3Y","5Y","10Y","20Y","All","Custom"],index=3,key="mode_"+key)
        if mode=="Custom":
            a,b=st.columns(2)
            start=a.date_input("From",date.today()-timedelta(days=365),key="from_"+key)
            end=b.date_input("To",date.today(),key="to_"+key)
        elif mode=="All": start,end=date(1900,1,1),date.today()
        else: start,end=date.today()-timedelta(days=365*int(mode[:-1])),date.today()
        cfg[key]=(pd.Timestamp(start),pd.Timestamp(end))
    chart=st.radio("Chart type",["Column","Line","Area"],horizontal=True)
    labels=st.checkbox("Show data labels",True)
cards=st.columns(5)
for i,key in enumerate(LABELS):
    with cards[i]:
        s=df[df.indicator==key] if not df.empty else df
        if not s.empty:
            last=s.sort_values("period_date").iloc[-1]
            st.metric(LABELS[key],f'{last["value"]:.2f} {last.get("unit","%")}',help=f'Period: {last["period_date"].date()}')
        else: st.metric(LABELS[key],"No data")
st.subheader("Historical charts")
cc=st.columns(2)
for i,key in enumerate(chosen):
    if df.empty: continue
    s=df[df.indicator==key].copy()
    if s.empty: continue
    start,end=cfg[key]
    s=s[(s.period_date>=start)&(s.period_date<=end)].sort_values("period_date")
    if s.empty:
        st.info(f"No observations in selected range: {LABELS[key]}")
        continue
    if chart=="Column": fig=px.bar(s,x="period_date",y="value",title=LABELS[key],text="value" if labels else None)
    elif chart=="Line": fig=px.line(s,x="period_date",y="value",title=LABELS[key],markers=True)
    else: fig=px.area(s,x="period_date",y="value",title=LABELS[key])
    fig.update_layout(height=320,margin=dict(l=10,r=10,t=45,b=10),xaxis_title=None,yaxis_title=s.iloc[-1].get("unit","Value"))
    with cc[i%2]: st.plotly_chart(fig,use_container_width=True)
st.subheader("Historical data and remarks")
if not df.empty:
    view=df[df.indicator.isin(chosen)].copy()
    view["indicator_label"]=view.indicator.map(LABELS).fillna(view.indicator)
    if "remarks" not in view: view["remarks"]=""
    edited=st.data_editor(view[["period_date","indicator_label","country","value","unit","release_date","source_name","source_url","remarks"]],hide_index=True,use_container_width=True,
        column_config={"period_date":st.column_config.DateColumn("Observation period",disabled=True),"indicator_label":st.column_config.TextColumn("Indicator",disabled=True),"country":st.column_config.TextColumn("Country",disabled=True),"value":st.column_config.NumberColumn("Value",disabled=True),"unit":st.column_config.TextColumn("Unit",disabled=True),"release_date":st.column_config.TextColumn("Release date",disabled=True),"source_name":st.column_config.TextColumn("Source",disabled=True),"source_url":st.column_config.LinkColumn("Source link",disabled=True),"remarks":st.column_config.TextColumn("Remarks (editable)",width="large")})
    st.download_button("Download remarks CSV",edited[["indicator_label","period_date","remarks"]].to_csv(index=False).encode(),"remarks.csv","text/csv")
    st.download_button("Download filtered observations",view.to_csv(index=False).encode(),"india_macro_observations.csv","text/csv")
else:
    st.warning("No observations loaded yet. Commit your existing Indian source files into data/source/ and run the GitHub Action.")
with st.expander("Official reference sources"):
    st.markdown("- [MoSPI — CPI and national statistics](https://www.mospi.gov.in/)\\n- [Office of Economic Adviser — WPI](https://eaindustry.nic.in/)\\n- [RBI — policy rates and announcements](https://www.rbi.org.in/)\\n- [RBI Database on Indian Economy](https://dbie.rbi.org.in/)")
