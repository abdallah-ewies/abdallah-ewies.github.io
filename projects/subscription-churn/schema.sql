DROP TABLE IF EXISTS customers; DROP TABLE IF EXISTS subscriptions;
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, signup_date TEXT NOT NULL, country TEXT, channel TEXT);
-- cancel_month is the first month in which the customer is no longer billed. NULL = still active on 2026-01-01.
CREATE TABLE subscriptions (customer_id INTEGER PRIMARY KEY REFERENCES customers, plan TEXT, monthly_price INTEGER, signup_date TEXT, cancel_month TEXT);
