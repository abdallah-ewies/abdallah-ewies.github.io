-- Q1 cohort retention: share of each signup-month cohort still billed N months after the first month.
-- A customer is billed in month m if signup_month <= m < cancel_month. Only months fully inside the observation window count.
-- name: cohort_retention
WITH base AS (
  SELECT customer_id, plan, monthly_price, date(signup_date,'start of month') AS cohort, cancel_month FROM subscriptions),
nums(n) AS (SELECT 0 UNION ALL SELECT n+1 FROM nums WHERE n < 23),
cohort_size AS (SELECT cohort, COUNT(*) AS size FROM base GROUP BY cohort),
alive AS (
  SELECT b.cohort, k.n AS month_n, COUNT(*) AS alive
  FROM base b JOIN nums k ON date(b.cohort, '+'||k.n||' months') < '2026-01-01'
   AND (b.cancel_month IS NULL OR date(b.cohort, '+'||k.n||' months') < b.cancel_month)
  GROUP BY b.cohort, k.n)
SELECT a.cohort, c.size, a.month_n, a.alive, ROUND(100.0*a.alive/c.size,1) AS retention_pct
FROM alive a JOIN cohort_size c USING (cohort) ORDER BY a.cohort, a.month_n;

-- Q2 monthly MRR roll-forward: opening + new - churned = closing, per month.
-- name: mrr_rollforward
WITH RECURSIVE months(m) AS (SELECT '2024-01-01' UNION ALL SELECT date(m,'+1 month') FROM months WHERE m < '2025-12-01'),
b AS (SELECT monthly_price AS p, date(signup_date,'start of month') AS s, cancel_month AS c FROM subscriptions)
SELECT m AS month,
  COALESCE((SELECT SUM(p) FROM b WHERE s < m AND (c IS NULL OR c >= m)),0) AS opening_mrr,
  COALESCE((SELECT SUM(p) FROM b WHERE s = m),0) AS new_mrr,
  COALESCE((SELECT SUM(p) FROM b WHERE c = m),0) AS churned_mrr,
  COALESCE((SELECT SUM(p) FROM b WHERE s <= m AND (c IS NULL OR c > m)),0) AS closing_mrr
FROM months ORDER BY m;

-- Q3 churn by plan and channel: cancelled / customer-months at risk (customer-months run to cancel_month or 2026-01-01).
-- name: churn_by_segment
WITH x AS (
  SELECT s.plan, c.channel,
    (CAST(strftime('%Y',COALESCE(s.cancel_month,'2026-01-01')) AS INT)*12 + CAST(strftime('%m',COALESCE(s.cancel_month,'2026-01-01')) AS INT))
   -(CAST(strftime('%Y',s.signup_date) AS INT)*12 + CAST(strftime('%m',s.signup_date) AS INT)) AS months_at_risk,
    CASE WHEN s.cancel_month IS NULL THEN 0 ELSE 1 END AS cancelled
  FROM subscriptions s JOIN customers c USING (customer_id))
SELECT plan, channel, COUNT(*) AS customers, SUM(cancelled) AS cancelled, SUM(months_at_risk) AS customer_months,
       ROUND(100.0*SUM(cancelled)/SUM(months_at_risk),2) AS monthly_churn_pct
FROM x GROUP BY plan, channel ORDER BY plan, channel;
