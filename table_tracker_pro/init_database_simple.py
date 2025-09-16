#!/usr/bin/env python3
import sqlite3
import os

# Database path
DB_PATH = '/home/h21s/table_tracker_pro/data/table_tracker.db'

print(f"🗄️ Creating database at: {DB_PATH}")

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Connect and create tables
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("📋 Creating tables...")

# Create customers table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        total_amount REAL DEFAULT 0.0,
        total_minutes REAL DEFAULT 0.0,
        snooker_amount REAL DEFAULT 0.0,
        snooker_minutes REAL DEFAULT 0.0,
        pool_amount REAL DEFAULT 0.0,
        pool_minutes REAL DEFAULT 0.0,
        today_amount REAL DEFAULT 0.0,
        today_minutes REAL DEFAULT 0.0,
        last_session_amount REAL DEFAULT 0.0,
        last_session_minutes REAL DEFAULT 0.0,
        last_session_time TIMESTAMP,
        last_updated_date TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create transactions table  
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_type TEXT NOT NULL,
        game_type TEXT,
        description TEXT,
        staff_user TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
''')

# Create sessions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        table_id INTEGER NOT NULL,
        game_type TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        duration_minutes REAL NOT NULL,
        amount REAL NOT NULL,
        rate REAL NOT NULL,
        staff_user TEXT,
        session_date TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
''')

print("📊 Adding sample customers...")

# Insert sample customers (only if table is empty)
cursor.execute('SELECT COUNT(*) FROM customers')
if cursor.fetchone()[0] == 0:
    customers = [
        ('John Doe', '9876543210'),
        ('Jane Smith', '9876543211'),
        ('Amit Kumar', '9876543212'),
        ('Priya Sharma', '9876543213'),
        ('Rahul Singh', '9876543214')
    ]
    
    for name, phone in customers:
        cursor.execute('INSERT INTO customers (name, phone) VALUES (?, ?)', (name, phone))
    
    print(f"✅ Added {len(customers)} sample customers")

# Commit changes
conn.commit()

# Verify
cursor.execute('SELECT COUNT(*) FROM customers')
customer_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM transactions') 
transaction_count = cursor.fetchone()[0]

print(f"✅ Database created successfully!")
print(f"👥 Customers: {customer_count}")
print(f"💰 Transactions: {transaction_count}")

conn.close()

# Check file size
size = os.path.getsize(DB_PATH)
print(f"📁 Database size: {size} bytes")
