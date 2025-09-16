import os

class Config:
    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'table_tracker.db')
    EXPORT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'customer_export.txt')
    
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 8080
    DEBUG = False  # DISABLED DEBUG MODE
    SECRET_KEY = 'table-tracker-pro-secret-key-2025'
    
    # Table Configuration
    SNOOKER_TABLES = {
        1: {"rate": 4.0},
        2: {"rate": 4.5}, 
        3: {"rate": 4.0}
    }
    
    POOL_TABLES = {
        1: {"rate": 2.0},
        2: {"rate": 2.5},
        3: {"rate": 2.0}
    }
    
    # Available rates for all tables (₹2.0 to ₹10.0)
    AVAILABLE_RATES = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
    
    # User Management
    DEFAULT_USERS = {
        'admin': {'password': 'admin123', 'role': 'admin'},
        'staff1': {'password': 'staff123', 'role': 'staff'}
    }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        os.makedirs(os.path.dirname(cls.DATABASE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(cls.EXPORT_PATH), exist_ok=True)
        print(f"✅ Data directory: {os.path.dirname(cls.DATABASE_PATH)}")
