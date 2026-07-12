DROP TABLE IF EXISTS activity_log;
DROP TABLE IF EXISTS maintenance_requests;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS allocations;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS asset_categories;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS users;

CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    head_id INTEGER,
    parent_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee',  -- employee | dept_head | asset_manager | admin
    department_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE asset_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    extra_fields TEXT  -- e.g. JSON string for warranty period, etc.
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_tag TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER,
    serial_number TEXT,
    status TEXT NOT NULL DEFAULT 'available',
    -- available | allocated | reserved | maintenance | lost | retired | disposed
    location TEXT,
    condition TEXT,
    is_bookable INTEGER NOT NULL DEFAULT 0,
    acquisition_cost REAL,
    acquisition_date TEXT,
    FOREIGN KEY (category_id) REFERENCES asset_categories(id)
);

CREATE TABLE allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    allocated_on TEXT NOT NULL DEFAULT (datetime('now')),
    expected_return TEXT,
    returned_on TEXT,
    status TEXT NOT NULL DEFAULT 'active',  -- active | returned | transferred
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (employee_id) REFERENCES users(id)
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_asset_id INTEGER NOT NULL,
    booked_by INTEGER NOT NULL,
    start_time TEXT NOT NULL,   -- format: 'YYYY-MM-DD HH:MM'
    end_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'upcoming',  -- upcoming | ongoing | completed | cancelled
    FOREIGN KEY (resource_asset_id) REFERENCES assets(id),
    FOREIGN KEY (booked_by) REFERENCES users(id)
);

CREATE TABLE maintenance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    raised_by INTEGER NOT NULL,
    issue TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',  -- low | medium | high
    status TEXT NOT NULL DEFAULT 'pending',
    -- pending | approved | rejected | in_progress | resolved
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (raised_by) REFERENCES users(id)
);

CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    target TEXT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
