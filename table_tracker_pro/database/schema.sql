-- Customers Table
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
    last_session_time DATETIME,
    last_updated_date DATE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    amount REAL,
    transaction_type TEXT,
    game_type TEXT,
    description TEXT,
    staff_user TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(customer_id) REFERENCES customers(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_total_amount ON customers(total_amount DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_date ON transactions(created_date);
CREATE INDEX IF NOT EXISTS idx_transactions_game_type ON transactions(game_type);
