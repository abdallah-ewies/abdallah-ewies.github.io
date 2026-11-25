# Income, health spending and life expectancy: Egypt in context

A demo portfolio project. Not client work.

**Question:** how much of the difference in life expectancy between countries lines up with income, and where does Egypt sit?

**Data:** World Bank World Development Indicators (API, 2000 to 2022): GDP per capita PPP (constant 2021 international $), life expectancy at birth, current health expenditure per capita (US$), population, infant mortality. Cite as World Bank, WDI. The World Bank data catalog lists CC BY 4.0 as the default licence and notes some datasets carry other licences; each indicator's licence was not individually checked.

**Run it:** `pip install pandas numpy matplotlib openpyxl xlsxwriter`, then `python3 wb_analysis.py` and `python3 build_xlsx.py`. The first run downloads the data into `data/`.

**Steps:** load and join country metadata, drop regional aggregates, report missing values by indicator, flag unusual life-expectancy values (kept), fit life expectancy on log income for 2019 with and without them, compute each country's gap to the trend, compare Egypt with its income group, chart.

**Primary result keeps every source value.** 9 life-expectancy values (Central African Republic in six years, Haiti 2010, Somalia 2011, South Sudan 2017) sit more than 8 years from the median of the same country's neighbouring years. For example Central African Republic reads 14.7 in 2009 and 31.5 in 2019 between values near 50. I compared the stored row with the live World Bank API (SP.DYN.LE00.IN, source WDI, last updated 2026-11-11): the values match, so the parser is not the cause and the series is published that way. I cannot tell from the data whether they are source errors or real shocks (Haiti 2010 matches the January 2010 earthquake). So nothing is removed from the main result. They are listed in `out/flagged_life_expectancy.csv` and marked on the chart.

**Sensitivity check (same fit without the flagged values, 2019):**

| | Primary (all source values) | Sensitivity (without flagged) |
|---|---|---|
| Countries | 199 | 198 |
| Years gained per doubling of income | 4.1 | 3.9 |
| R squared | 0.715 | 0.734 |
| Egypt gap to trend | -1.4 years | -1.6 years |
| Egypt rank by gap, 46 lower-middle-income countries | 30th | 28th |

The Egypt conclusion does not change.

**Results (primary, 2019, 199 countries):** each doubling of income goes with about 4.1 more years of life expectancy (R squared 0.715). Egypt: 71.2 years against 72.6 expected from income, a gap of -1.4 years. Egypt gained 3.9 years from 2000 to 2019; the median for its income group was 6.7. Egypt's health spending was about $143 per person against a group median of $71 (the Excel summary shows the group mean, $124).

**Sources by indicator (as listed in the World Bank indicator metadata):** GDP per capita PPP, NY.GDP.PCAP.PP.KD, from the International Comparison Program. Life expectancy, SP.DYN.LE00.IN, from UN World Population Prospects and national statistical offices. Health expenditure per capita, SH.XPD.CHEX.PC.CD, from the WHO Global Health Expenditure Database. Population, SP.POP.TOTL, UN World Population Prospects and national statistical offices. Infant mortality, SP.DYN.IMRT.IN, UN Inter-agency Group for Child Mortality Estimation. All are distributed in WDI. The World Bank API does not list a licence per indicator, so the dataset-level default (CC BY 4.0) is what I rely on. Attribution to the World Bank and the original source organisations is given here.

**Limits:** a cross-country association, not a cause. Small states and conflict settings produce large gaps, and some published life-expectancy values are unusual (see above). One year (2019) was chosen to avoid COVID effects on later life expectancy. Health spending is a level, not an efficiency measure.

**Files:** `wb_analysis.py`, `build_xlsx.py`, `out/wb-summary.xlsx` (summary figures are live formulas over the data sheet), `out/*.csv`, `out/*.png`.
