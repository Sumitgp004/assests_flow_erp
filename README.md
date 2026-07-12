# AssetFlow

## Setup (each teammate runs this after cloning)
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
python seed.py                # creates assetflow.db with demo data
python app.py                 # runs on http://127.0.0.1:5000
```

## Demo logins
| Email | Password | Role |
|---|---|---|
| admin@assetflow.com | admin123 | Admin |
| manager@assetflow.com | manager123 | Asset Manager |
| head@assetflow.com | head123 | Dept Head |
| priya@assetflow.com | priya123 | Employee — holds asset AF-0001 |
| raj@assetflow.com | raj123 | Employee — booked Room B2, 9-10am today |

## Pre-loaded test scenarios
- Try allocating AF-0001 (Dell Laptop) to anyone — it's blocked because Priya already holds it.
- Try booking Room B2 for 9:30-10:30 — rejected, overlaps Raj's 9:00-10:00 booking.
- Try booking Room B2 for 10:00-11:00 — accepted, starts right after the existing slot ends.

## Who owns what (see routes/ folder — one file per person)
- routes/auth.py, routes/allocation.py, routes/booking.py — Sumit
- routes/org.py, routes/assets.py, routes/maintenance.py — P2
- routes/logs.py + templates styling — P5
- schema.sql + seed.py — P3

## Branch workflow
Create a branch per task (`feature/xxx`), commit often, push, open a PR into `main`.
Merge `feature/base-template` and `feature/schema-seed` first — everything else depends on them.


the demo login.html and index .html files just mistakely created