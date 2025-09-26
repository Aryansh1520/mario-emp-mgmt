# db.py
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any

DEFAULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_code TEXT UNIQUE,
    name TEXT NOT NULL,
    designation TEXT,
    department TEXT,
    bank_account TEXT,
    ifsc TEXT,
    pan TEXT,
    joining_date TEXT,
    notes TEXT,

    -- Static earnings & deductions
    basic REAL DEFAULT 0.0,
    hra REAL DEFAULT 0.0,
    LTA REAL DEFAULT 0.0,
    special_allowance REAL DEFAULT 0.0,
    income_tax REAL DEFAULT 0.0,

    status TEXT DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS payslips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    pay_period TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY(employee_id) REFERENCES employees(id)
);
"""

# ------------------- Connection -------------------
def get_conn(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db(db_path: Path, seed_sample: bool = True) -> None:
    conn = get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(DEFAULT_SCHEMA)
        conn.commit()
        if seed_sample:
            cur.execute("SELECT COUNT(1) as cnt FROM employees")
            _ = cur.fetchone()
    finally:
        conn.close()

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()} if row else {}

# ------------------- Financials -------------------
def compute_financials(emp_data: dict) -> dict:
    basic = float(emp_data.get("basic", 0.0) or 0.0)
    hra = float(emp_data.get("hra", 0.0) or 0.0)
    LTA = float(emp_data.get("LTA", 0.0) or 0.0)
    special = float(emp_data.get("special_allowance", 0.0) or 0.0)
    income_tax = float(emp_data.get("income_tax", 0.0) or 0.0)

    gross = basic + hra + LTA + special
    net = gross - income_tax

    return {
        "basic": basic,
        "hra": hra,
        "LTA": LTA,
        "special_allowance": special,
        "income_tax": income_tax,
        "gross": round(gross, 2),
        "net": round(net, 2)
    }

# ------------------- Employee CRUD -------------------
def insert_employee(conn_or_path, payload: Dict[str, Any]) -> int:
    """Insert a new employee."""
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    sql = """
    INSERT INTO employees
    (emp_code, name, designation, department, bank_account, ifsc, pan, joining_date, notes,
     basic, hra, LTA, special_allowance, income_tax, status)
    VALUES
    (:emp_code, :name, :designation, :department, :bank_account, :ifsc, :pan, :joining_date, :notes,
     :basic, :hra, :LTA, :special_allowance, :income_tax, :status)
    """
    cur = conn.cursor()
    cur.execute(sql, payload)
    conn.commit()
    rowid = cur.lastrowid
    if close_conn:
        conn.close()
    return rowid

def update_employee(conn_or_path, emp_id: int, payload: Dict[str, Any]) -> bool:
    """Update an employee by id."""
    allowed = [
        "emp_code", "name", "designation", "department", "bank_account", "ifsc", "pan",
        "joining_date", "notes", "basic", "hra", "LTA", "special_allowance", "income_tax", "status"
    ]

    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    updates = []
    params = {"id": emp_id}
    for k in allowed:
        if k in payload:
            updates.append(f"{k} = :{k}")
            params[k] = payload[k]

    if not updates:
        if close_conn:
            conn.close()
        return False

    sql = f"UPDATE employees SET {', '.join(updates)} WHERE id = :id"
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    changed = cur.rowcount > 0
    if close_conn:
        conn.close()
    return changed

def delete_employee(conn_or_path, emp_id: int) -> bool:
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
    conn.commit()
    changed = cur.rowcount > 0
    if close_conn:
        conn.close()
    return changed

def get_all_employees(conn_or_path) -> List[Dict[str, Any]]:
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("SELECT * FROM employees ORDER BY name COLLATE NOCASE")
    rows = cur.fetchall()
    result = [row_to_dict(r) for r in rows]
    if close_conn:
        conn.close()
    return result

def get_active_employees(conn_or_path) -> List[Dict[str, Any]]:
    """Return all employees with status='Active'."""
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE status='Active' ORDER BY name COLLATE NOCASE")
    rows = cur.fetchall()
    result = [row_to_dict(r) for r in rows]
    if close_conn:
        conn.close()
    return result

def get_departments(conn_or_path) -> List[str]:
    """Return a list of unique departments."""
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("SELECT DISTINCT department FROM employees WHERE department IS NOT NULL")
    rows = cur.fetchall()
    departments = [r[0] for r in rows if r[0]]
    if close_conn:
        conn.close()
    return departments

def get_employee_by_id(conn_or_path, emp_id: int) -> Optional[Dict[str, Any]]:
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
    row = cur.fetchone()
    res = row_to_dict(row) if row else None
    if close_conn:
        conn.close()
    return res

# ------------------- Payslip CRUD -------------------
def insert_payslip(conn_or_path, employee_id: int, pay_period: str, notes: str = "") -> int:
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    sql = """
    INSERT INTO payslips (employee_id, pay_period, notes)
    VALUES (:employee_id, :pay_period, :notes)
    """
    cur = conn.cursor()
    cur.execute(sql, {
        "employee_id": employee_id,
        "pay_period": pay_period,
        "notes": notes
    })
    conn.commit()
    rowid = cur.lastrowid
    if close_conn:
        conn.close()
    return rowid

def get_payslip(conn_or_path, employee_id: int, pay_period: str) -> Optional[Dict[str, Any]]:
    close_conn = False
    if isinstance(conn_or_path, (str, Path)):
        conn = get_conn(Path(conn_or_path))
        close_conn = True
    else:
        conn = conn_or_path

    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, e.*,
               (e.basic + e.hra + e.LTA + e.special_allowance) AS gross,
               ((e.basic + e.hra + e.LTA + e.special_allowance) - e.income_tax) AS net
        FROM payslips p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.employee_id = ? AND p.pay_period = ?
    """, (employee_id, pay_period))
    row = cur.fetchone()
    res = row_to_dict(row) if row else None
    if close_conn:
        conn.close()
    return res
