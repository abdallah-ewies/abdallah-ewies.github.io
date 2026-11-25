"""Synthetic subscription data generator. ALL DATA IS INVENTED. Seeded, so reruns give the same file.
Churn behaviour is set by the hazard table below, so findings describe this generator, not a real business."""
import sqlite3, random, datetime as dt
random.seed(42)
PLANS = {"Starter": 19, "Pro": 49, "Team": 129}                      # monthly price, USD
PLAN_MIX = {"Starter": .55, "Pro": .33, "Team": .12}
CHANNELS = {"Organic": .35, "Paid search": .30, "Referral": .20, "Partner": .15}
BASE_CHURN = {"Starter": .075, "Pro": .045, "Team": .025}            # monthly cancel probability
CHANNEL_MULT = {"Organic": .9, "Paid search": 1.35, "Referral": .7, "Partner": 1.0}
COUNTRIES = ["US", "UK", "DE", "EG", "AE", "IN"]
START, END = dt.date(2024, 1, 1), dt.date(2025, 12, 1)               # signup months; observation ends 2026-01-01
OBS_END = dt.date(2026, 1, 1)
def pick(d): return random.choices(list(d), weights=d.values())[0]
def add_months(d, n): y, m = divmod(d.month - 1 + n, 12); return dt.date(d.year + y, m + 1, 1)
db = sqlite3.connect("churn.db"); db.executescript(open("schema.sql").read())
cid, rows_c, rows_s = 0, [], []
months = (END.year - START.year) * 12 + END.month - START.month + 1
for i in range(months):
    m0 = add_months(START, i); n = int(150 + i * 9 + random.randint(-15, 15))   # growing signups
    for _ in range(n):
        cid += 1; plan, ch = pick(PLAN_MIX), pick(CHANNELS)
        signup = m0 + dt.timedelta(days=random.randint(0, 27)); rows_c.append((cid, signup.isoformat(), pick({c: 1 for c in COUNTRIES}), ch))
        p = BASE_CHURN[plan] * CHANNEL_MULT[ch]; start = m0; k = 0; cancel = None
        while add_months(start, k + 1) <= OBS_END:
            k += 1; haz = p * (2.2 if k == 1 else 1.4 if k <= 3 else 1.0)    # early-life churn is higher
            if random.random() < min(haz, .9): cancel = add_months(start, k); break
        rows_s.append((cid, plan, PLANS[plan], signup.isoformat(), cancel.isoformat() if cancel else None))
db.executemany("INSERT INTO customers VALUES (?,?,?,?)", rows_c); db.executemany("INSERT INTO subscriptions VALUES (?,?,?,?,?)", rows_s); db.commit()
print(len(rows_c), "customers", sum(1 for r in rows_s if r[4] is None), "active at", OBS_END)
