# India Macro Indicator Dashboard

India-only version. US CPI/Fed series have been removed.

## Indicators
- India CPI inflation (YoY)
- India WPI inflation (YoY)
- RBI policy repo rate
- RBI fixed reverse repo rate
- RBI SDF rate (included separately because it is the current floor-rate instrument; do not confuse it with fixed reverse repo)

## Use your uploaded GitHub data files
Put the files you uploaded into `data/source/` (CSV or XLSX). The collector scans that folder every day and attempts to normalize rows. Each file should have columns that identify:
- indicator or series name
- date/period
- value
- optionally release date, source URL and remarks

Recommended column names are `indicator`, `period_date` (or `date`/`period`), `value`, `release_date`, `source_url`, `source_name`, `remarks`. Indicator names can be `india_cpi_yoy`, `india_wpi_yoy`, `rbi_repo`, `rbi_reverse_repo`, `rbi_sdf`.

If your uploaded files have different columns/layouts, edit `ALIASES` in `collect_india.py` to match their exact headings. The collector does not invent values. It retains previously collected observations when no new file data is found.

## Setup
1. Upload this folder's contents into your existing GitHub repository (or replace the prior prototype files). Preserve `.github/workflows/refresh-india.yml`.
2. In GitHub repository Settings → Actions → General, allow read/write repository contents.
3. Actions → `Refresh Indian macro data` → Run workflow to test.
4. Deploy `app.py` on Streamlit Community Cloud, pointing to the same repository.

## Official reference sources
- MoSPI / CPI: https://www.mospi.gov.in/
- Office of Economic Adviser / WPI: https://eaindustry.nic.in/
- RBI policy rates and releases: https://www.rbi.org.in/
- RBI Database on Indian Economy: https://dbie.rbi.org.in/

## Important
The workflow auto-processes files committed to `data/source/`. It does not automatically download every Indian series from the official websites yet, because the relevant official sources have different publication formats and may require stable API/feed configuration. It will not treat a source webpage as a data feed unless a supported collector is implemented. Verify all values against official releases before trading.
