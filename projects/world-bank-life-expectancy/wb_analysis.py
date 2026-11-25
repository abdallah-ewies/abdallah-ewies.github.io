"""Income, health spending and life expectancy, 2000-2022 (World Bank WDI).
Run: python3 wb_analysis.py   (downloads data once into ./data, then reuses it)
Outputs: ./out/*.csv and ./out/*.png
Data: World Bank, World Development Indicators, licensed CC BY 4.0 (https://datacatalog.worldbank.org/public-licenses)."""
import json, os, urllib.request
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

IND = {"gdp_pc": "NY.GDP.PCAP.PP.KD", "life_exp": "SP.DYN.LE00.IN", "health_pc": "SH.XPD.CHEX.PC.CD",
       "pop": "SP.POP.TOTL", "infant_mort": "SP.DYN.IMRT.IN"}
os.makedirs("data", exist_ok=True); os.makedirs("out", exist_ok=True)

def fetch(url, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return json.load(open(path))

# 1. Load ------------------------------------------------------------------
meta = fetch("https://api.worldbank.org/v2/country?format=json&per_page=400", "data/countries.json")[1]
cmeta = pd.DataFrame([{"iso3": c["id"], "country": c["name"], "region": c["region"]["value"], "income_group": c["incomeLevel"]["value"]} for c in meta])
cmeta = cmeta[cmeta.region != "Aggregates"]            # drop regional and income aggregates such as "World"
frames = []
for name, code in IND.items():
    d = fetch(f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&date=2000:2022", f"data/{code}.json")[1]
    frames.append(pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), name: r["value"]} for r in d if r["countryiso3code"]]).set_index(["iso3", "year"]))
panel = pd.concat(frames, axis=1).reset_index().merge(cmeta, on="iso3", how="inner")

# 2. Data quality ---------------------------------------------------------
dq = {"countries (non-aggregate)": panel.iso3.nunique(), "country-years": len(panel)}
for c in IND: dq[f"missing {c}"] = int(panel[c].isna().sum())
# Some life-expectancy values swing sharply (e.g. Central African Republic reads 14.7 in 2009 and 31.5 in 2019 between values near 50).
# They match what the World Bank API publishes (checked against the live API for CAF), so they are NOT proven errors and may be real shocks.
# The PRIMARY results keep every source value. A SENSITIVITY fit without them is reported beside it. Flag a value that differs by more than 8 years from the median of the same country's other values within 2 years.
panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
def neighbour_median(g):
    v = g.life_exp.values; out = []
    for i in range(len(v)):
        nb = [v[j] for j in range(max(0, i - 2), min(len(v), i + 3)) if j != i and not np.isnan(v[j])]
        out.append(np.median(nb) if nb else np.nan)
    return pd.Series(out, index=g.index)
panel["le_neighbour_median"] = panel.groupby("iso3", group_keys=False).apply(neighbour_median)
panel["le_flag"] = (panel.life_exp - panel.le_neighbour_median).abs() > 8
panel[panel.le_flag][["iso3", "country", "year", "life_exp", "le_neighbour_median"]].round(1).to_csv("out/flagged_life_expectancy.csv", index=False)
dq["life-expectancy values flagged as extreme year-to-year swings (kept in primary results, left out of the sensitivity fit)"] = int(panel.le_flag.sum())
pd.Series(dq, name="value").to_csv("out/data_quality.csv")
panel["life_exp_sens"] = panel.life_exp.where(~panel.le_flag)
complete = panel.dropna(subset=["gdp_pc", "life_exp"])
dq["country-years with income and life expectancy (primary, all source values)"] = len(complete)
pd.Series(dq, name="value").to_csv("out/data_quality.csv")
cov = panel.groupby("year")[["gdp_pc", "life_exp", "health_pc"]].apply(lambda g: g.notna().mean().round(2)); cov.to_csv("out/coverage_by_year.csv")

# 3. Income-health curve (2019, last year before COVID distorted life expectancy) -----
y = complete[complete.year == 2019].copy()
y["ln_gdp"] = np.log(y.gdp_pc)
b1, b0 = np.polyfit(y.ln_gdp, y.life_exp, 1)
y["expected_le"] = b0 + b1 * y.ln_gdp
y["gap_years"] = y.life_exp - y.expected_le                # positive = lives longer than income predicts
r2 = np.corrcoef(y.ln_gdp, y.life_exp)[0, 1] ** 2
y.sort_values("gap_years").to_csv("out/gap_2019.csv", index=False)
res = {"n_countries_2019": len(y), "slope_years_per_doubling_of_income": round(b1 * np.log(2), 2), "r2": round(r2, 3)}

# Sensitivity: same fit without the flagged values
ys = y.dropna(subset=["life_exp_sens"]); s1, s0 = np.polyfit(ys.ln_gdp, ys.life_exp_sens, 1)
sens_exp = s0 + s1 * np.log(y.gdp_pc); sens_gap = y.life_exp - sens_exp
peers_all = y[y.income_group == y[y.iso3 == "EGY"].income_group.iloc[0]]
res["sensitivity_without_flagged"] = {"n_countries_2019": len(ys), "slope_years_per_doubling_of_income": round(s1 * np.log(2), 2),
    "r2": round(np.corrcoef(ys.ln_gdp, ys.life_exp_sens)[0, 1] ** 2, 3)}
y["gap_sens"] = sens_gap

# 4. Progress 2000 -> 2019 -------------------------------------------------
a = complete[complete.year == 2000].set_index("iso3"); b = complete[complete.year == 2019].set_index("iso3")
prog = pd.DataFrame({"country": b.country, "region": b.region, "income_group": b.income_group,
                     "le_2000": a.life_exp, "le_2019": b.life_exp, "gdp_2000": a.gdp_pc, "gdp_2019": b.gdp_pc}).dropna()
prog["le_gain"] = prog.le_2019 - prog.le_2000
prog["gdp_growth_pct"] = (prog.gdp_2019 / prog.gdp_2000 - 1) * 100
prog.sort_values("le_gain", ascending=False).to_csv("out/progress_2000_2019.csv")

# 5. Egypt in context ----------------------------------------------------
eg = y[y.iso3 == "EGY"].iloc[0]
peers = y[(y.income_group == eg.income_group)]
res.update({"egypt_le_2019": round(eg.life_exp, 1), "egypt_expected_le": round(eg.expected_le, 1), "egypt_gap": round(eg.gap_years, 1),
            "egypt_income_group": eg.income_group, "egypt_rank_gap_in_income_group": int((peers.gap_years > eg.gap_years).sum() + 1), "income_group_size": len(peers),
            "egypt_gap_sensitivity": round(float(y.loc[y.iso3 == "EGY", "gap_sens"].iloc[0]), 1),
            "egypt_rank_sensitivity": int((peers.gap_sens > y.loc[y.iso3 == "EGY", "gap_sens"].iloc[0]).sum() + 1),
            "egypt_le_gain_2000_2019": round(prog.loc["EGY", "le_gain"], 1), "median_gain_same_group": round(prog[prog.income_group == eg.income_group].le_gain.median(), 1)})
hs = panel[(panel.year == 2019)].dropna(subset=["health_pc", "life_exp"])
res["egypt_health_spend_pc_2019"] = round(float(hs[hs.iso3 == "EGY"].health_pc.iloc[0]), 0)
res["median_health_spend_same_group"] = round(float(hs[hs.income_group == eg.income_group].health_pc.median()), 0)
json.dump(res, open("out/results.json", "w"), indent=1)

# 6. Charts -------------------------------------------------------------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.scatter(y.gdp_pc, y.life_exp, s=22, c="#b7c9c4", edgecolor="none", label="Countries")
xs = np.linspace(y.ln_gdp.min(), y.ln_gdp.max(), 100); ax.plot(np.exp(xs), b0 + b1 * xs, c="#251f21", lw=1.5, label="Trend")
ax.plot(np.exp(xs), s0 + s1 * xs, c="#c46a5a", lw=1.2, ls="--", label="Trend without 2019 flagged values (sensitivity)")
fl19 = y[y.le_flag]; ax.scatter(fl19.gdp_pc, fl19.life_exp, s=40, facecolor="none", edgecolor="#c46a5a", zorder=4, label="Flagged source values (kept)")
ax.scatter([eg.gdp_pc], [eg.life_exp], s=90, c="#2f7f6f", zorder=5, label="Egypt")
ax.annotate(f"Egypt: {eg.life_exp:.1f} years\n(trend says {eg.expected_le:.1f})", (eg.gdp_pc, eg.life_exp), xytext=(18, -45), textcoords="offset points", arrowprops=dict(arrowstyle="-", color="#2f7f6f"))
ax.set_xscale("log"); ax.set_xlabel("GDP per capita, PPP (constant 2021 intl $, log scale)"); ax.set_ylabel("Life expectancy at birth (years)")
ax.set_title("Richer countries live longer, with large exceptions (2019)", loc="left"); ax.legend(frameon=False, loc="lower right", fontsize=9)
fig.text(0.01, 0.005, "Source: World Bank WDI (life expectancy: UN WPP and national statistics offices; GDP per capita PPP), 2019. Cross-country association, no causation.\nLog-linear fit by least squares. Small states and conflict settings sit far from the trend. Solid line keeps all source values.", fontsize=7.5, color="#555", va="bottom")
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig("out/income_vs_life_expectancy.png", dpi=150); plt.close(fig)

top = y.sort_values("gap_years"); sel = pd.concat([top.head(7), top.tail(7)])
fig, ax = plt.subplots(figsize=(9, 5.5)); ax.barh(sel.country, sel.gap_years, color=["#c46a5a" if v < 0 else "#2f7f6f" for v in sel.gap_years]); ax.axvline(0, c="#251f21", lw=.8)
ax.set_xlabel("Years of life expectancy above (+) or below (-) what income predicts"); ax.set_title("Biggest gaps between income and life expectancy (2019)", loc="left")
fig.text(0.01, 0.005, "Source: World Bank WDI, 2019. Gap = actual minus value predicted from log income (all source values kept). No causation.\nSome extreme gaps are small states, conflict settings or unusual published values (see flagged_life_expectancy.csv).", fontsize=7.5, color="#555", va="bottom")
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig("out/biggest_gaps.png", dpi=150); plt.close(fig)
print(json.dumps(res, indent=1)); print(sel[["country", "income_group", "life_exp", "expected_le", "gap_years"]].round(1).to_string(index=False))
