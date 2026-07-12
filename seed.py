"""
Run this once to create assetflow.db with demo data.
Includes the two scenarios named in the problem statement so you can
demo the conflict rules live:
  - Priya holds Laptop AF-0001 -> Raj trying to allocate it should be BLOCKED
  - Room B2 is booked 09:00-10:00 today -> a 09:30-10:30 request should be
    REJECTED, a 10:00-11:00 request should be ACCEPTED
"""
import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("assetflow.db")
conn.executescript(open("schema.sql").read())
cur = conn.cursor()


def add_user(name, email, password, role, dept_id=None):
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role, department_id) VALUES (?, ?, ?, ?, ?)",
        (name, email, generate_password_hash(password), role, dept_id),
    )
    return cur.lastrowid


# --- Departments ---
cur.execute("INSERT INTO departments (name, status) VALUES ('IT', 'active')")
it_dept = cur.lastrowid
cur.execute("INSERT INTO departments (name, status) VALUES ('Operations', 'active')")
ops_dept = cur.lastrowid

# --- Users (one per role, plus Priya/Raj for the demo scenario) ---
admin_id = add_user("Admin User", "admin@assetflow.com", "admin123", "admin", it_dept)
manager_id = add_user("Asset Manager", "manager@assetflow.com", "manager123", "asset_manager", it_dept)
head_id = add_user("Dept Head", "head@assetflow.com", "head123", "dept_head", ops_dept)
priya_id = add_user("Priya Sharma", "priya@assetflow.com", "priya123", "employee", ops_dept)
raj_id = add_user("Raj Verma", "raj@assetflow.com", "raj123", "employee", ops_dept)

cur.execute("UPDATE departments SET head_id = ? WHERE id = ?", (head_id, ops_dept))

# --- Categories ---
cur.execute("INSERT INTO asset_categories (name) VALUES ('Electronics')")
electronics = cur.lastrowid
cur.execute("INSERT INTO asset_categories (name) VALUES ('Rooms')")
rooms = cur.lastrowid

# --- Assets ---
cur.execute("""INSERT INTO assets
    (asset_tag, name, category_id, serial_number, status, location, condition, is_bookable, acquisition_cost, acquisition_date)
    VALUES ('AF-0001', 'Dell Laptop', ?, 'SN-1001', 'available', 'IT Store', 'Good', 0, 55000, '2025-01-10')""",
    (electronics,))
laptop_id = cur.lastrowid

cur.execute("""INSERT INTO assets
    (asset_tag, name, category_id, serial_number, status, location, condition, is_bookable, acquisition_cost, acquisition_date)
    VALUES ('AF-0002', 'Room B2', ?, NULL, 'available', 'Block B', 'Good', 1, 0, '2024-06-01')""",
    (rooms,))
room_b2_id = cur.lastrowid

cur.execute("""INSERT INTO assets
    (asset_tag, name, category_id, serial_number, status, location, condition, is_bookable, acquisition_cost, acquisition_date)
    VALUES ('AF-0003', 'MacBook Pro', ?, 'SN-1002', 'available', 'IT Store', 'New', 0, 150000, '2026-02-01')""",
    (electronics,))

# --- Demo scenario 1: Priya already holds the laptop ---
cur.execute("""INSERT INTO allocations (asset_id, employee_id, expected_return, status)
    VALUES (?, ?, '2026-08-01', 'active')""", (laptop_id, priya_id))
cur.execute("UPDATE assets SET status = 'allocated' WHERE id = ?", (laptop_id,))

# --- Demo scenario 2: Room B2 booked 09:00-10:00 today ---
cur.execute("""INSERT INTO bookings (resource_asset_id, booked_by, start_time, end_time, status)
    VALUES (?, ?, '2026-07-12 09:00', '2026-07-12 10:00', 'upcoming')""", (room_b2_id, raj_id))

conn.commit()
conn.close()

print("Seeded assetflow.db\n")
print("Demo logins (all passwords match the pattern below):")
print("  admin@assetflow.com   / admin123    (Admin)")
print("  manager@assetflow.com / manager123  (Asset Manager)")
print("  head@assetflow.com    / head123     (Dept Head)")
print("  priya@assetflow.com   / priya123    (Employee - holds AF-0001)")
print("  raj@assetflow.com     / raj123      (Employee - booked Room B2 9-10am)")
