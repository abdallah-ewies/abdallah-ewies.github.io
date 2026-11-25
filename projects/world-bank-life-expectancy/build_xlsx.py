"""Builds out/wb-summary.xlsx from the CSVs written by wb_analysis.py. Summary numbers are live Excel formulas."""
import pandas as pd, xlsxwriter
g = pd.read_csv("out/gap_2019.csv"); p = pd.read_csv("out/progress_2000_2019.csv"); f = pd.read_csv("out/flagged_life_expectancy.csv"); dq = pd.read_csv("out/data_quality.csv", index_col=0).iloc[:, 0]
wb = xlsxwriter.Workbook("out/wb-summary.xlsx")
H = wb.add_format({"bold": True, "bg_color": "#2f7f6f", "font_color": "white", "border": 1, "text_wrap": True, "valign": "top"})
T = wb.add_format({"bold": True, "font_size": 14}); N = wb.add_format({"num_format": "0.0"}); N2 = wb.add_format({"num_format": "0.00"}); W = wb.add_format({"text_wrap": True, "valign": "top"}); B = wb.add_format({"bold": True})
# Data sheet
d = wb.add_worksheet("Data_2019"); cols = ["iso3", "country", "region", "income_group", "gdp_pc", "life_exp", "health_pc", "infant_mort"]
for j, c in enumerate(cols + ["ln_gdp (formula)", "expected_le (formula)", "gap_years (formula)", "life_exp_sensitivity (flagged left blank)"]): d.write(0, j, c, H)
n = len(g)
for i, r in enumerate(g[cols].itertuples(index=False), start=1):
    for j, v in enumerate(r):
        if pd.isna(v): continue
        d.write(i, j, v)
    d.write_formula(i, 8, f"=LN(E{i+1})", N2); d.write_formula(i, 9, f"=Summary!$B$7+Summary!$B$6*I{i+1}", N); d.write_formula(i, 10, f"=F{i+1}-J{i+1}", N)
    if not g.le_flag.iloc[i-1]: d.write(i, 11, g.life_exp.iloc[i-1])
d.freeze_panes(1, 2); d.set_column(0, 0, 7); d.set_column(1, 3, 22); d.set_column(4, 11, 16); d.autofilter(0, 0, n, 11)
last = n + 1
# Summary
s = wb.add_worksheet("Summary"); s.set_column(0, 0, 58); s.set_column(1, 1, 18); s.set_column(2, 2, 70)
s.write(0, 0, "Income, health spending and life expectancy: Egypt in context (World Bank WDI, 2019)", T)
s.write(1, 0, "Cross-country association only. It does not show that income causes longer life. Data: World Bank WDI, 2019, cited with attribution. Primary results keep every published value; the sensitivity block leaves out the flagged ones.", W)
rows = [
 ("Countries in the 2019 sample", f"=COUNT(Data_2019!F2:F{last})", "All source values kept (primary result). Sensitivity without flagged values is below."),
 ("Years of life expectancy gained per doubling of income", f"=SLOPE(Data_2019!F2:F{last},Data_2019!I2:I{last})*LN(2)", "Slope of life expectancy on ln(income), times ln 2"),
 ("Slope per ln(income)", f"=SLOPE(Data_2019!F2:F{last},Data_2019!I2:I{last})", ""),
 ("Intercept", f"=INTERCEPT(Data_2019!F2:F{last},Data_2019!I2:I{last})", ""),
 ("R squared", f"=RSQ(Data_2019!F2:F{last},Data_2019!I2:I{last})", "Share of variation in life expectancy that income (log) accounts for"),
 ("Egypt life expectancy", '=INDEX(Data_2019!F2:F%d,MATCH("EGY",Data_2019!A2:A%d,0))' % (last, last), "Years"),
 ("Egypt expected by the trend", '=INDEX(Data_2019!J2:J%d,MATCH("EGY",Data_2019!A2:A%d,0))' % (last, last), "Years"),
 ("Egypt gap (actual minus trend)", '=INDEX(Data_2019!K2:K%d,MATCH("EGY",Data_2019!A2:A%d,0))' % (last, last), "Negative means below what income predicts"),
 ("Lower-middle-income countries in sample", f'=COUNTIF(Data_2019!D2:D{last},"Lower middle income")', ""),
 ("Of those, how many have a gap below Egypt's (worse)", f'=COUNTIFS(Data_2019!D2:D{last},"Lower middle income",Data_2019!K2:K{last},"<"&B11)', ""),
 ("Egypt health spend per person, current US$", '=INDEX(Data_2019!G2:G%d,MATCH("EGY",Data_2019!A2:A%d,0))' % (last, last), "2019"),
 ("Average health spend per person, lower-middle-income group", f'=AVERAGEIFS(Data_2019!G2:G{last},Data_2019!D2:D{last},"Lower middle income")', "Mean, countries with data. The Python script reports the median ($71)."),
]
for k, (a, b, c) in enumerate(rows):
    s.write(3 + k - 0 if False else 3 + k, 0, a); s.write_formula(3 + k, 1, b, N2 if k in (2, 3, 4) else N); s.write(3 + k, 2, c, W)
r0 = 3 + len(rows) + 1
s.write(r0, 0, "Sensitivity: same fit without the flagged life-expectancy values", B)
s.write(r0+1, 0, "Countries"); s.write_formula(r0+1, 1, f"=COUNT(Data_2019!L2:L{last})", N)
s.write(r0+2, 0, "Years gained per doubling of income"); s.write_formula(r0+2, 1, f"=SLOPE(Data_2019!L2:L{last},Data_2019!I2:I{last})*LN(2)", N2)
s.write(r0+3, 0, "R squared"); s.write_formula(r0+3, 1, f"=RSQ(Data_2019!L2:L{last},Data_2019!I2:I{last})", N2)
s.write(r0+5, 0, "Biggest gaps: use the filter on column K of Data_2019", B)
# fix references: rows start at row index 3 => Excel row 4. B5=slope per doubling? ensure Data formulas point to slope(row 6) and intercept(row 7)
# Progress, Flagged, Quality
pr = wb.add_worksheet("Progress_2000_2019"); pc = ["country", "region", "income_group", "le_2000", "le_2019", "le_gain", "gdp_2000", "gdp_2019", "gdp_growth_pct"]
for j, c in enumerate(pc): pr.write(0, j, c, H)
for i, r in enumerate(p[pc].itertuples(index=False), start=1):
    for j, v in enumerate(r):
        if not pd.isna(v): pr.write(i, j, v)
pr.freeze_panes(1, 1); pr.set_column(0, 2, 24); pr.set_column(3, 8, 14); pr.autofilter(0, 0, len(p), 8)
fl = wb.add_worksheet("Flagged"); fl.write(0, 0, "Life-expectancy values that sit more than 8 years from the median of the same country's neighbouring years. They match what the World Bank API publishes, so they are unusual source values, not proven errors. The primary results keep them; the Summary sheet shows the fit without them as a sensitivity check. Haiti 2010 coincides with the January 2010 earthquake and may be a real observation.", W); fl.set_row(0, 48)
for j, c in enumerate(f.columns): fl.write(2, j, c, H)
for i, r in enumerate(f.itertuples(index=False), start=3):
    for j, v in enumerate(r): fl.write(i, j, v)
fl.set_column(0, 4, 24)
q = wb.add_worksheet("Data_quality"); q.write(0, 0, "check", H); q.write(0, 1, "value", H)
for i, (k, v) in enumerate(dq.items(), start=1): q.write(i, 0, k); q.write(i, 1, v)
q.set_column(0, 0, 70)
wb.close()
