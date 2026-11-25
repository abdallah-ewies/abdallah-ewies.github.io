"""Builds budget-cashflow-model.xlsx: a 12-month budget and cash-flow model for a FICTIONAL small coffee-subscription business.
All numbers are invented assumptions. Every calculated cell is a live Excel formula; change the scenario on the Inputs sheet."""
import sys, xlsxwriter
scen_default = sys.argv[1] if len(sys.argv) > 1 else "Base"
out = sys.argv[2] if len(sys.argv) > 2 else "budget-cashflow-model.xlsx"
wb = xlsxwriter.Workbook(out)
F = lambda **k: wb.add_format({"font_name": "Calibri", "font_size": 10, **k})
title, h, lab, bold = F(bold=True, font_size=16, font_color="#251f21"), F(bold=True, bg_color="#2f7f6f", font_color="white", border=1, align="center", valign="vcenter", text_wrap=True), F(), F(bold=True)
inp = F(font_color="#0000ff", bg_color="#fff8e1", border=1); inp_pct = F(font_color="#0000ff", bg_color="#fff8e1", border=1, num_format="0.0%"); inp_cur = F(font_color="#0000ff", bg_color="#fff8e1", border=1, num_format="$#,##0.00")
inp_int = F(font_color="#0000ff", bg_color="#fff8e1", border=1, num_format="#,##0")
cur, cur0, pct, intf = F(num_format="$#,##0;[Red]-$#,##0"), F(num_format="$#,##0;[Red]-$#,##0", bold=True, top=1), F(num_format="0.0%"), F(num_format="#,##0")
note = F(italic=True, font_color="#555555", text_wrap=True, valign="top"); calc_pct = F(num_format="0.0%", bg_color="#e8f1ee", border=1); calc_cur = F(num_format="$#,##0.00", bg_color="#e8f1ee", border=1); calc_int = F(num_format="#,##0", bg_color="#e8f1ee", border=1)
SCEN = ["Base", "Optimistic", "Downside"]
# name, label, base, optimistic, downside, kind
A = [("units0", "Units sold in month 1 (bags)", 600, 650, 480, "int"),
     ("growth", "Monthly unit growth", .05, .07, .01, "pct"),
     ("price", "Price per bag", 22.0, 22.5, 21.0, "cur"),
     ("cogs", "Cost of goods as % of revenue", .52, .50, .56, "pct"),
     ("collect", "Share of revenue collected in the month of sale", .70, .75, .60, "pct"),
     ("rent", "Rent per month", 1800, 1800, 1800, "cur"),
     ("salary", "Salaries per month", 3500, 3500, 3500, "cur"),
     ("mkt", "Marketing per month", 900, 1200, 700, "cur"),
     ("capex", "Equipment purchase (one-off)", 4000, 4000, 4000, "cur"),
     ("capex_m", "Equipment purchase month (1-12)", 3, 3, 3, "int"),
     ("cash0", "Opening cash", 15000, 15000, 15000, "cur")]
R = {a[0]: 6 + i for i, a in enumerate(A)}   # 0-based row index of each assumption on Inputs
# ---- Inputs sheet
ws = wb.add_worksheet("Inputs"); ws.set_column(0, 0, 3); ws.set_column(1, 1, 50); ws.set_column(2, 5, 15); ws.set_column(6, 6, 60)
ws.write(0, 1, "Budget and cash-flow model: Inputs", title)
ws.merge_range(1, 1, 1, 6, "DEMO WITH INVENTED NUMBERS for a fictional coffee-subscription business. Not a real company, not advice.", note)
ws.write(3, 1, "Active scenario (pick from list)", bold); ws.write(3, 2, scen_default, F(bold=True, font_color="#0000ff", bg_color="#ffe0b2", border=2))
ws.data_validation(3, 2, 3, 2, {"validate": "list", "source": SCEN})
for j, t in enumerate(["Assumption"] + SCEN + ["Active", "Notes"]): ws.write(5, 1 + j, t, h)
kinds = {"int": (inp_int, calc_int), "pct": (inp_pct, calc_pct), "cur": (inp_cur, calc_cur)}
notes = {"collect": "The rest is collected the following month.", "capex_m": "Paid in cash that month, not expensed.", "growth": "Compounded month on month.", "cogs": "Paid in the month of sale."}
for a in A:
    r = R[a[0]]; ws.write(r, 1, a[1], lab)
    for j in range(3): ws.write(r, 2 + j, a[2 + j], kinds[a[5]][0])
    ws.write_formula(r, 5, f"=INDEX(C{r+1}:E{r+1},MATCH($C$4,$C$6:$E$6,0))", kinds[a[5]][1]); ws.write(r, 6, notes.get(a[0], ""), note)
ws.merge_range(R["cash0"] + 2, 1, R["cash0"] + 2, 6, "Blue cells on cream are inputs. Green cells are formulas. Everything else in the workbook is calculated from them.", note)
# ---- model builder
def model(name, col):    # col: letter on Inputs holding the assumptions to use
    s = wb.add_worksheet(name); s.set_column(0, 0, 36); s.set_column(1, 13, 11); s.freeze_panes(2, 1)
    I = lambda k: f"Inputs!${col}${R[k]+1}"
    s.write(0, 0, f"Monthly budget and cash flow ({'active scenario' if col == 'F' else name.replace('Calc_', '') + ' scenario'})", bold)
    s.write(1, 0, "Month", h)
    for m in range(12): s.write(1, 1 + m, m + 1, h)
    s.write(1, 13, "Year", h)
    rows = ["Units sold", "Revenue", "Cost of goods", "Gross profit", "Rent", "Salaries", "Marketing", "Operating profit",
            "Cash collected from customers", "Cash paid: cost of goods and operating costs", "Equipment purchase", "Net cash flow", "Opening cash", "Closing cash"]
    for i, t in enumerate(rows): s.write(2 + i, 0, t, bold if t in ("Gross profit", "Operating profit", "Closing cash") else lab)
    for m in range(12):
        c = chr(66 + m); p = chr(65 + m); r = lambda k: f"{c}{k}"
        s.write_formula(2, 1 + m, f"={I('units0')}*(1+{I('growth')})^({c}$2-1)", intf)
        s.write_formula(3, 1 + m, f"={c}3*{I('price')}", cur)
        s.write_formula(4, 1 + m, f"={c}4*{I('cogs')}", cur)
        s.write_formula(5, 1 + m, f"={c}4-{c}5", cur0)
        s.write_formula(6, 1 + m, f"={I('rent')}", cur); s.write_formula(7, 1 + m, f"={I('salary')}", cur); s.write_formula(8, 1 + m, f"={I('mkt')}", cur)
        s.write_formula(9, 1 + m, f"={c}6-{c}7-{c}8-{c}9", cur0)
        prev = "0" if m == 0 else f"{p}4"
        s.write_formula(10, 1 + m, f"={c}4*{I('collect')}+{prev}*(1-{I('collect')})", cur)
        s.write_formula(11, 1 + m, f"={c}5+{c}7+{c}8+{c}9", cur)
        s.write_formula(12, 1 + m, f"=IF({c}$2={I('capex_m')},{I('capex')},0)", cur)
        s.write_formula(13, 1 + m, f"={c}11-{c}12-{c}13", cur0)
        s.write_formula(14, 1 + m, f"={I('cash0')}" if m == 0 else f"={p}16", cur)
        s.write_formula(15, 1 + m, f"={c}15+{c}14", cur0)
    for rr in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14):
        if rr == 15: continue
        s.write_formula(rr - 1, 13, f"=SUM(B{rr}:M{rr})", cur0 if rr in (6, 10, 14) else (intf if rr == 3 else cur))
    s.merge_range(17, 0, 18, 13, "Revenue is earned in the month of sale. Customers who do not pay in the month pay in the next month, so the last month's unpaid share is still owed at year end and is not in cash.", note)
    return s
M = model("Model", "F"); model("Calc_Base", "C"); model("Calc_Optimistic", "D"); model("Calc_Downside", "E")
# ---- Summary
S = wb.add_worksheet("Summary"); S.set_column(0, 0, 44); S.set_column(1, 4, 16)
S.write(0, 0, "Summary", title); S.write(1, 0, "Scenario shown:", bold); S.write_formula(1, 1, "=Inputs!C4", F(bold=True, font_color="#2f7f6f"))
kp = [("Year revenue", "=Model!N4", cur), ("Year gross profit", "=Model!N6", cur), ("Year operating profit", "=Model!N10", cur),
      ("Gross margin", "=Model!N6/Model!N4", pct), ("Closing cash, month 12", "=Model!M16", cur),
      ("Lowest closing cash in the year", "=MIN(Model!B16:M16)", cur),
      ("Month of lowest cash", "=MATCH(MIN(Model!B16:M16),Model!B16:M16,0)", intf),
      ("First month with operating profit above zero", '=IFERROR(MATCH(TRUE,INDEX(Model!B10:M10>0,0),0),"none in 12 months")', intf),
      ("Cash runs out in the year?", '=IF(MIN(Model!B16:M16)<0,"YES","No")', F(bold=True))]
S.write(3, 0, "Key results (active scenario)", h); S.write(3, 1, "Value", h)
for i, (a, f, fm) in enumerate(kp): S.write(4 + i, 0, a, lab); S.write_formula(4 + i, 1, f, fm)
r0 = 4 + len(kp) + 1
S.write(r0, 0, "All three scenarios side by side", h)
for j, t in enumerate(SCEN): S.write(r0, 1 + j, t, h)
cmp_rows = [("Year revenue", "N4", cur), ("Year operating profit", "N10", cur), ("Closing cash, month 12", "M16", cur), ("Lowest closing cash", "MIN(Calc_{}!B16:M16)", cur)]
for i, (a, ref, fm) in enumerate(cmp_rows):
    S.write(r0 + 1 + i, 0, a, lab)
    for j, sc in enumerate(SCEN):
        f = f"=Calc_{sc}!{ref}" if "{}" not in ref else "=" + ref.format(sc)
        S.write_formula(r0 + 1 + i, 1 + j, f, fm)
ch = wb.add_chart({"type": "column"}); ch.add_series({"name": "Revenue", "categories": "=Model!$B$2:$M$2", "values": "=Model!$B$4:$M$4", "fill": {"color": "#b7c9c4"}})
ch.add_series({"name": "Operating profit", "categories": "=Model!$B$2:$M$2", "values": "=Model!$B$10:$M$10", "fill": {"color": "#2f7f6f"}})
ln = wb.add_chart({"type": "line"}); ln.add_series({"name": "Closing cash", "categories": "=Model!$B$2:$M$2", "values": "=Model!$B$16:$M$16", "line": {"color": "#251f21", "width": 2.25}})
ch.combine(ln); ch.set_title({"name": "Revenue, operating profit and closing cash (active scenario)", "name_font": {"size": 11}}); ch.set_x_axis({"name": "Month"}); ch.set_y_axis({"num_format": "$#,##0"}); ch.set_legend({"position": "bottom"}); ch.set_size({"width": 700, "height": 340})
S.insert_chart(r0 + 7, 0, ch)
S.merge_range(r0 + 26, 0, r0 + 26, 4, "Demo with invented numbers. The scenarios are assumptions, not forecasts.", note)
for w in wb.worksheets(): w.set_landscape(); w.fit_to_pages(1, 1)
wb.close()
