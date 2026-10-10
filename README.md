# Macro Indicator Dashboard

GitHub Actions + Streamlit starter for India CPI/WPI, RBI repo/reverse repo, and US Fed Funds Rate. Independent date ranges per indicator, column/line/area charts, comparison, and editable remarks.

## Setup
1. Upload all files in this folder to a new GitHub repository.
2. Add repository secret `FRED_API_KEY` (free key: https://fred.stlouisfed.org/docs/api/api_key.html).
3. Settings → Actions → General → Workflow permissions: allow read/write contents.
4. Actions → Refresh macro data → Run workflow.
5. Deploy `app.py` on https://share.streamlit.io/ using this repository.

## Data source notes
The collector fetches official FRED series: `FEDFUNDS` (US effective federal funds rate) and `CPIAUCSL` (US CPI index converted to year-over-year change). This is US CPI, not India CPI.
India CPI, India WPI, RBI repo and reverse repo are left for verified official observations because a stable, public machine-readable feed should be confirmed before automating them. Sources: https://www.mospi.gov.in/ , https://eaindustry.nic.in/ , https://www.rbi.org.in/

`data/observations.csv` columns: `indicator,country,period_date,release_date,value,unit,source_url,source_name,remarks`.
Indicator keys: `india_cpi_yoy`, `india_wpi_yoy`, `us_fed_funds`, `us_cpi_yoy`, `rbi_repo`, `rbi_reverse_repo`.
Use numeric percentages (e.g. `5.5`), ISO dates (`YYYY-MM-DD`). For policy rates, period_date is effective date; release_date is publication date.

## Remarks persistence
Edit remarks in the dashboard and download `remarks.csv`; commit it to the repository to persist. Streamlit Cloud local files are not guaranteed persistent, so this version does not pretend dashboard edits are automatically committed to GitHub.

## Schedule
Daily at 07:30 IST (02:00 UTC). GitHub can delay scheduled runs during high load. Change cron in `.github/workflows/refresh.yml` if needed.

This is an economic research tool, not a trading signal. Verify source values and dates before trading.
