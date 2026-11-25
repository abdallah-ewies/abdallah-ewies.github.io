# Small-business budget and cash-flow model (Excel)

**Demo portfolio project with INVENTED numbers** for a fictional coffee-subscription business. Not client work, not a forecast.

**What it does:** a 12-month budget and cash-flow model with a scenario switch. Pick Base, Optimistic or Downside in the orange cell on `Inputs` and the `Model` and `Summary` sheets update. Every calculated cell is a live formula. Blue-on-cream cells are inputs; green cells show the active scenario's values.

**Sheets:** `Inputs` (assumptions for three scenarios plus the switch), `Model` (units, revenue, cost of goods, operating costs, operating profit, cash collected with a one-month collection lag, equipment purchase, opening and closing cash), `Summary` (key results, three scenarios side by side, chart), and three `Calc_` sheets that hold each scenario's model so the side-by-side table is live.

**Checks done:** I rebuilt all three scenarios independently in Python and compared them with Excel's recalculated results (LibreOffice). Revenue, operating profit, closing cash and lowest cash match in all three. Excel computes the values when the file is opened.

**What the demo shows (invented inputs):** Base ends the year with $30.7k cash after a dip to $8.0k in month 3 (equipment purchase) and turns operating profit positive in month 1. Optimistic ends at $56.1k. Downside never reaches operating profit and cash falls to -$9.2k by month 12, which the Summary flags as "cash runs out".

**Limits:** one product line, flat fixed costs, no tax, no loan, no inventory build, no seasonality. Cost of goods and operating costs are paid in the month incurred. These are simplifications for a demo; a real client model would start from their own figures.
