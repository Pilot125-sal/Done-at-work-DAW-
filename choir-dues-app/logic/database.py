import os
import sys
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

# Determine base path for database file
if getattr(sys, 'frozen', False):
    # Running as exe
    base_path = os.path.dirname(sys.executable)
else:
    # Running as script
    base_path = os.path.dirname(__file__)

# DB_NAME = "data/payments.db" #replaced with the following lines below to ensure compatibility with exe

DB_NAME = os.path.join(base_path, "data", "payments.db")


MONTHLY_DUE = 5


def connect():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT,
        amount REAL,
        month TEXT,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_payment(member_name, amount, month, note=""):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (member_name, amount, month, note)
        VALUES (?, ?, ?, ?)
    """, (member_name, amount, month, note))

    conn.commit()
    conn.close()

def add_payment_auto(member_name, total_amount, start_month="01-2026", monthly_due=5, note=""):
    """
    Auto-allocate total_amount to consecutive months starting from start_month.
    Each month gets up to monthly_due until the total_amount is exhausted.
    """
    month = datetime.strptime(start_month, "%m-%Y")
    
    while total_amount > 0:
        month_str = month.strftime("%m-%Y")
        pay_for_month = min(monthly_due, total_amount)
        add_payment(member_name, pay_for_month, month_str, note)
        total_amount -= pay_for_month
        month += relativedelta(months=1)

def get_all_payments():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT member_name, amount, month, note FROM payments")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Delete a payment by row id
def delete_payment(payment_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()

# Edit a payment by id
def edit_payment(payment_id, member_name, amount, month, note):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE payments
        SET member_name = ?, amount = ?, month = ?, note = ?
        WHERE id = ?
    """, (member_name, amount, month, note, payment_id))
    conn.commit()
    conn.close()

# Fetch payments with id included
def get_all_payments_with_id():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, member_name, amount, month, note FROM payments")
    rows = cursor.fetchall()
    conn.close()
    return rows
   

def allocate_and_save(name, amount, start_month, end_month, note="", monthly_due=MONTHLY_DUE):
    conn = connect()
    cursor = conn.cursor()
    start = datetime.strptime(start_month, "%m-%Y")
    end = datetime.strptime(end_month, "%m-%Y")

    months = []
    current = start
    while current <= end:
        months.append(current.strftime("%m-%Y"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    expected_total = len(months) * MONTHLY_DUE
    if amount != expected_total:
      raise ValueError(f"Expected €{expected_total} for {len(months)} months")

    for m in months:
        add_payment(name, MONTHLY_DUE, m, note)
    conn.commit()
    conn.close()

def delete_member(member_name): # Delete all payments for a specific member, added on 19.01.2026
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments WHERE member_name = ?", (member_name,))
    conn.commit()
    conn.close()    

# # Fetch payments for a specific member
# def get_payments_by_member(member_name):
#     conn = connect()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, month, amount, note FROM payments WHERE member_name = ?", (member_name,))
#     rows = cursor.fetchall()
#     conn.close()
#     return rows