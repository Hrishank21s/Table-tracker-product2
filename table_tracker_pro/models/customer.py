import sqlite3
import shutil
import os
from datetime import datetime, date
from config import Config

class CustomerModel:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.export_path = Config.EXPORT_PATH
        self.backup_dir = "/home/h21s/table_tracker_pro/backups"
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self._reset_daily_amounts()
        print(f"✅ Customer Model initialized - DB: {self.db_path}")
    
    def _create_backup(self, operation=""):
        """Create automatic backup of database"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"auto_backup_{operation}_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                print(f"💾 Auto-backup created: {backup_filename}")
                
                # Clean old auto-backups (keep last 5)
                auto_backups = [f for f in os.listdir(self.backup_dir) if f.startswith("auto_backup_")]
                auto_backups.sort(reverse=True)
                
                for old_backup in auto_backups[5:]:
                    old_path = os.path.join(self.backup_dir, old_backup)
                    os.remove(old_path)
                    
        except Exception as e:
            print(f"⚠️ Auto-backup failed: {e}")
    
    def _reset_daily_amounts(self):
        """Reset today's amounts if it's a new day"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            today = date.today().isoformat()
            
            c.execute("""UPDATE customers SET 
                         today_amount = 0.0, 
                         today_minutes = 0.0,
                         last_updated_date = ?
                         WHERE last_updated_date != ? OR last_updated_date IS NULL""", 
                      (today, today))
            conn.commit()
            conn.close()
            print(f"✅ Daily amounts reset for new day: {today}")
        except Exception as e:
            print(f"⚠️ Failed to reset daily amounts: {e}")
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def add_customer(self, name, phone):
        try:
            conn = self.get_connection()
            c = conn.cursor()
            today = date.today().isoformat()
            c.execute("INSERT INTO customers (name, phone, last_updated_date) VALUES (?, ?, ?)", 
                     (name, phone, today))
            customer_id = c.lastrowid
            conn.commit()
            conn.close()
            
            # Auto-backup on new customer
            self._create_backup("add_customer")
            return customer_id
        except sqlite3.IntegrityError:
            return None
    
    def search_customers(self, search_term):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name", 
                  (f'%{search_term}%', f'%{search_term}%'))
        customers = c.fetchall()
        conn.close()
        return customers
    
    def get_all_customers(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM customers ORDER BY total_amount DESC")
        customers = c.fetchall()
        conn.close()
        return customers
    
    def add_amount_to_customer(self, customer_id, amount, minutes, description, staff_user, game_type):
        conn = self.get_connection()
        c = conn.cursor()
        today = date.today().isoformat()
        
        if game_type == 'snooker':
            c.execute("""UPDATE customers SET 
                         total_amount = total_amount + ?,
                         total_minutes = total_minutes + ?,
                         snooker_amount = COALESCE(snooker_amount, 0) + ?,
                         snooker_minutes = COALESCE(snooker_minutes, 0) + ?,
                         today_amount = COALESCE(today_amount, 0) + ?,
                         today_minutes = COALESCE(today_minutes, 0) + ?,
                         last_session_amount = ?,
                         last_session_minutes = ?,
                         last_session_time = CURRENT_TIMESTAMP,
                         last_updated_date = ?
                         WHERE id = ?""", 
                      (amount, minutes, amount, minutes, amount, minutes, 
                       amount, minutes, today, customer_id))
        else:  # pool
            c.execute("""UPDATE customers SET 
                         total_amount = total_amount + ?,
                         total_minutes = total_minutes + ?,
                         pool_amount = COALESCE(pool_amount, 0) + ?,
                         pool_minutes = COALESCE(pool_minutes, 0) + ?,
                         today_amount = COALESCE(today_amount, 0) + ?,
                         today_minutes = COALESCE(today_minutes, 0) + ?,
                         last_session_amount = ?,
                         last_session_minutes = ?,
                         last_session_time = CURRENT_TIMESTAMP,
                         last_updated_date = ?
                         WHERE id = ?""", 
                      (amount, minutes, amount, minutes, amount, minutes,
                       amount, minutes, today, customer_id))
        
        c.execute("INSERT INTO transactions (customer_id, amount, transaction_type, game_type, description, staff_user) VALUES (?, ?, ?, ?, ?, ?)",
                  (customer_id, amount, 'session', game_type, description, staff_user))
        
        conn.commit()
        conn.close()
        
        # Auto-backup on session completion (important data)
        self._create_backup("session_complete")
    
    def adjust_customer_balance(self, customer_id, amount, transaction_type, staff_user):
        conn = self.get_connection()
        c = conn.cursor()
        today = date.today().isoformat()
        
        c.execute("""UPDATE customers SET 
                     total_amount = total_amount + ?,
                     today_amount = COALESCE(today_amount, 0) + ?,
                     last_updated_date = ?
                     WHERE id = ?""", (amount, amount, today, customer_id))
        
        description = f"Manual {'addition' if amount > 0 else 'subtraction'} by {staff_user}"
        c.execute("INSERT INTO transactions (customer_id, amount, transaction_type, description, staff_user) VALUES (?, ?, ?, ?, ?)",
                  (customer_id, amount, transaction_type, description, staff_user))
        
        conn.commit()
        conn.close()
        
        # Auto-backup on balance adjustment
        self._create_backup("balance_adjust")
    
    def get_today_stats(self):
        conn = self.get_connection()
        c = conn.cursor()
        today = date.today().isoformat()
        
        c.execute("SELECT COUNT(*) FROM customers")
        total_customers = c.fetchone()[0]
        
        c.execute("SELECT SUM(COALESCE(today_amount, 0)), SUM(COALESCE(today_minutes, 0)) FROM customers WHERE last_updated_date = ?", (today,))
        today_total = c.fetchone()
        
        c.execute("SELECT SUM(amount) FROM transactions WHERE DATE(created_date) = ? AND game_type = 'snooker'", (today,))
        snooker_today = c.fetchone()[0] or 0
        
        c.execute("SELECT SUM(amount) FROM transactions WHERE DATE(created_date) = ? AND game_type = 'pool'", (today,))
        pool_today = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_customers': total_customers,
            'today_total_amount': today_total[0] or 0,
            'today_total_minutes': today_total[1] or 0,
            'today_snooker_amount': snooker_today,
            'today_pool_amount': pool_today
        }
    
    def get_top_customers(self, limit=5):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT name, total_amount FROM customers ORDER BY total_amount DESC LIMIT ?", (limit,))
        top_customers = c.fetchall()
        conn.close()
        return top_customers
    
    def export_to_txt(self):
        try:
            customers = self.get_all_customers()
            os.makedirs(os.path.dirname(self.export_path), exist_ok=True)
            
            with open(self.export_path, 'w') as f:
                f.write("="*80 + "\n")
                f.write("TABLE TRACKER PRO - CUSTOMER DATA EXPORT\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(f"TOTAL CUSTOMERS: {len(customers)}\n")
                f.write(f"EXPORT FILE: {self.export_path}\n")
                f.write(f"DATABASE: {self.db_path}\n\n")
                
                if customers:
                    f.write(f"{'ID':<5} {'NAME':<25} {'PHONE':<15} {'TOTAL':<12} {'SNOOKER':<12} {'POOL':<12}\n")
                    f.write("-" * 83 + "\n")
                    
                    for customer in customers:
                        f.write(f"{customer[0]:<5} {customer[1][:24]:<25} {customer[2]:<15} "
                               f"₹{customer[3]:<11.2f} ₹{customer[5] or 0:<11.2f} ₹{customer[7] or 0:<11.2f}\n")
                else:
                    f.write("No customers found.\n")
            
            print(f"✅ Customer data exported to: {self.export_path}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
