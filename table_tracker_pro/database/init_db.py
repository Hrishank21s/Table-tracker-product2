import sqlite3
import os
from config import Config

def init_database():
    """Initialize the database with required tables"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    print(f"🗄️ Initializing database at: {Config.DATABASE_PATH}")
    
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
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
    
    # Create sessions table (for completed sessions)
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
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers (phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_name ON customers (name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions (customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (created_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions (session_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_customer ON sessions (customer_id)')
    
    # Insert sample data if database is empty
    cursor.execute('SELECT COUNT(*) FROM customers')
    customer_count = cursor.fetchone()[0]
    
    if customer_count == 0:
        print("📊 Adding sample customers...")
        sample_customers = [
            ('John Doe', '9876543210'),
            ('Jane Smith', '9876543211'),
            ('Amit Kumar', '9876543212'),
            ('Priya Sharma', '9876543213'),
            ('Rahul Singh', '9876543214')
        ]
        
        for name, phone in sample_customers:
            cursor.execute('INSERT INTO customers (name, phone) VALUES (?, ?)', (name, phone))
            
        print(f"✅ Added {len(sample_customers)} sample customers")
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialization completed successfully!")
    print(f"📁 Database location: {Config.DATABASE_PATH}")
    
    # Verify database was created
    if os.path.exists(Config.DATABASE_PATH):
        size = os.path.getsize(Config.DATABASE_PATH)
        print(f"📊 Database size: {size} bytes")
        
        # Quick verification
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM transactions")
        transaction_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"👥 Customers: {customer_count}")
        print(f"💰 Transactions: {transaction_count}")
    else:
        print("❌ Database file was not created!")

if __name__ == "__main__":
    init_database()
