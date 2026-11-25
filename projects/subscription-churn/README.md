# Subscription churn by cohort, in SQL

**Demo portfolio project on SYNTHETIC data. Not client work, not a real business.**

**Question:** for a made-up subscription product, how fast do customers cancel, which plans and channels churn most, and how does recurring revenue (MRR) move month to month?

**Data:** `generate_data.py` creates 6,040 invented customers (signups Jan 2024 to Dec 2025, observed to 1 Jan 2026) in SQLite with a fixed random seed, so a rerun gives the same file. Churn depends on plan, channel and customer age through a small hazard table written in the script. That means every finding below describes the generator, which is the point of a demo: it lets the SQL be checked against a known answer. It says nothing about real customers.

**Run it:** `python3 generate_data.py` then `python3 run_queries.py` (needs pandas, numpy, matplotlib). SQL lives in `schema.sql` and `queries.sql`.

**SQL used:** CTEs, a recursive month series, joins on computed month offsets, conditional aggregation, correlated subqueries for the MRR roll-forward, and date arithmetic.

**Checks in the script:** opening MRR + new MRR - churned MRR equals closing MRR in every month, and signup dates agree between the two tables.

**What the output shows (synthetic):**
- Early life is the weak point: the January 2024 cohort keeps 87% after 1 month, 63% after 6 and 29% after 23 months.
- Starter churns about 9.7% of customer-months, Pro 5.2%, Team 3.0%.
- Paid-search customers churn most inside every plan (Starter 13.4%, Pro 7.1%, Team 3.9%); referral customers churn least (6.3%, 3.4%, 1.8%).
- Closing MRR reaches about $161.6k in December 2025. Churned MRR grows with the base, from $0.5k in Feb 2024 to $7.2k in Dec 2025.

**Limits:** churn rate here is cancellations divided by customer-months at risk. Customers are billed monthly at a fixed list price; there are no discounts, upgrades or refunds. Cancel dates are month-level.

**Files:** `generate_data.py`, `schema.sql`, `queries.sql`, `run_queries.py`, `churn.db`, `out/*.csv` and three charts in `out/`.
