from datetime import datetime
from config import Config
import threading
import time
import sqlite3
import os

class TableManager:
    def __init__(self):
        self.snooker_tables = {}
        self.pool_tables = {}
        self.available_rates = Config.AVAILABLE_RATES
        self.running = True
        
        print("🎯 Initializing Table Manager with session persistence...")
        
        # Initialize snooker tables
        for table_id, config in Config.SNOOKER_TABLES.items():
            self.snooker_tables[table_id] = {
                "status": "idle",
                "time": "00:00",
                "rate": config["rate"],
                "amount": 0.0,
                "start_time": None,
                "elapsed_seconds": 0,
                "sessions": [],
                "session_start_time": None,
                "last_update": None
            }
        
        # Initialize pool tables
        for table_id, config in Config.POOL_TABLES.items():
            self.pool_tables[table_id] = {
                "status": "idle",
                "time": "00:00", 
                "rate": config["rate"],
                "amount": 0.0,
                "start_time": None,
                "elapsed_seconds": 0,
                "sessions": [],
                "session_start_time": None,
                "last_update": None
            }
        
        # Load recent sessions from database
        self.load_recent_sessions()
        
        print(f"✅ Initialized {len(self.snooker_tables)} Snooker tables: {list(self.snooker_tables.keys())}")
        print(f"✅ Initialized {len(self.pool_tables)} Pool tables: {list(self.pool_tables.keys())}")
        
        # Start timer thread with precise timing
        self.timer_thread = threading.Thread(target=self.update_timers, daemon=True)
        self.timer_thread.start()
        print("⏰ Precise timer system started with session persistence")
    
    def get_db_connection(self):
        """Get database connection"""
        return sqlite3.connect(Config.DATABASE_PATH)
    
    def save_session_to_db(self, table_id, game_type, session_data):
        """Save completed session to database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions 
                (table_id, game_type, start_time, end_time, duration_minutes, amount, rate, staff_user, session_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                table_id,
                game_type,
                session_data['start_time'],
                session_data['end_time'],
                session_data['duration'],
                session_data['amount'],
                session_data.get('rate', 0),
                session_data.get('user', 'system'),
                session_data['date']
            ))
            
            conn.commit()
            conn.close()
            print(f"💾 Session saved to database: {game_type} Table {table_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save session to database: {e}")
            return False
    
    def load_recent_sessions(self):
        """Load recent sessions from database (last 3 per table)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Load recent sessions for each table
            for game_type in ['snooker', 'pool']:
                tables = self.get_tables(game_type)
                
                for table_id in tables.keys():
                    cursor.execute('''
                        SELECT start_time, end_time, duration_minutes, amount, session_date
                        FROM sessions 
                        WHERE table_id = ? AND game_type = ?
                        ORDER BY created_date DESC 
                        LIMIT 3
                    ''', (table_id, game_type))
                    
                    sessions = cursor.fetchall()
                    tables[table_id]['sessions'] = []
                    
                    for session in sessions:
                        tables[table_id]['sessions'].append({
                            'start_time': session[0],
                            'end_time': session[1],
                            'duration': session[2],
                            'amount': session[3],
                            'date': session[4]
                        })
                    
                    if sessions:
                        print(f"📊 Loaded {len(sessions)} recent sessions for {game_type} Table {table_id}")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Could not load recent sessions: {e}")
    
    def get_tables(self, game_type):
        """Get tables for specific game type"""
        if game_type == 'snooker':
            result = self.snooker_tables
        elif game_type == 'pool':
            result = self.pool_tables
        else:
            result = {}
        
        return result
    
    def handle_table_action(self, game_type, table_id, action, username):
        """Handle table actions (start, pause, end)"""
        print(f"🎮 Table action: {game_type} Table {table_id} - {action} by {username}")
        
        tables = self.get_tables(game_type)
        
        if table_id not in tables:
            return {"success": False, "message": f"Invalid table ID: {table_id}"}
        
        table = tables[table_id]
        current_time = datetime.now()
        
        if action == 'start':
            if table['status'] == 'idle':
                table['status'] = 'running'
                table['start_time'] = current_time
                table['last_update'] = current_time
                table['elapsed_seconds'] = 0
                table['session_start_time'] = current_time.strftime("%H:%M:%S")
                print(f"✅ Started {game_type} Table {table_id}")
                return {
                    "success": True,
                    "message": f"{game_type.title()} Table {table_id} started",
                    "show_customer_popup": False
                }
            elif table['status'] == 'paused':
                table['status'] = 'running'
                table['last_update'] = current_time
                return {
                    "success": True,
                    "message": f"{game_type.title()} Table {table_id} resumed",
                    "show_customer_popup": False
                }
        
        elif action == 'pause':
            if table['status'] == 'running':
                table['status'] = 'paused'
                # Update elapsed time when pausing
                if table['last_update']:
                    time_diff = (current_time - table['last_update']).total_seconds()
                    table['elapsed_seconds'] += int(time_diff)
                    table['last_update'] = current_time
                return {
                    "success": True,
                    "message": f"{game_type.title()} Table {table_id} paused",
                    "show_customer_popup": False
                }
        
        elif action == 'end':
            if table['status'] in ['running', 'paused']:
                # Final time calculation
                if table['status'] == 'running' and table['last_update']:
                    time_diff = (current_time - table['last_update']).total_seconds()
                    table['elapsed_seconds'] += int(time_diff)
                
                duration_minutes = table['elapsed_seconds'] / 60
                amount = duration_minutes * table['rate']
                end_time = current_time.strftime("%H:%M:%S")
                
                session = {
                    "start_time": table.get('session_start_time', '00:00:00'),
                    "end_time": end_time,
                    "duration": round(duration_minutes, 1),
                    "amount": round(amount, 2),
                    "date": current_time.strftime("%Y-%m-%d"),
                    "user": username,
                    "game_type": game_type,
                    "rate": table['rate']
                }
                
                # Save session to database for persistence
                self.save_session_to_db(table_id, game_type, session)
                
                # Add to table's recent sessions (keep last 3)
                table['sessions'].append(session)
                if len(table['sessions']) > 3:
                    table['sessions'] = table['sessions'][-3:]
                
                # Reset table state
                table['status'] = 'idle'
                table['time'] = '00:00'
                table['amount'] = 0
                table['start_time'] = None
                table['elapsed_seconds'] = 0
                table['session_start_time'] = None
                table['last_update'] = None
                
                print(f"✅ Ended {game_type} Table {table_id} - ₹{amount:.2f} for {duration_minutes:.1f}min - SAVED TO DB")
                
                return {
                    "success": True,
                    "message": f"{game_type.title()} Table {table_id} ended - ₹{amount:.2f} for {duration_minutes:.1f} minutes",
                    "show_customer_popup": True,
                    "session_data": session
                }
        
        return {"success": False, "message": "No action taken"}
    
    def update_table_rate(self, game_type, table_id, new_rate):
        """Update table rate"""
        tables = self.get_tables(game_type)
        
        if table_id not in tables:
            return {"success": False, "message": "Invalid table ID"}
        
        if new_rate not in self.available_rates:
            return {"success": False, "message": "Invalid rate"}
        
        table = tables[table_id]
        
        if table['status'] != 'idle':
            return {"success": False, "message": "Cannot change rate while table is running"}
        
        table['rate'] = new_rate
        print(f"✅ Updated {game_type} Table {table_id} rate to ₹{new_rate}/min")
        return {"success": True, "message": f"Rate updated to ₹{new_rate}/min"}
    
    def clear_table_sessions(self, game_type, table_id):
        """Clear recent sessions display (not database)"""
        tables = self.get_tables(game_type)
        
        if table_id not in tables:
            return {"success": False, "message": "Invalid table ID"}
        
        tables[table_id]['sessions'] = []
        print(f"✅ Cleared recent sessions display for {game_type} Table {table_id}")
        return {"success": True, "message": "Recent sessions display cleared"}
    
    def update_timers(self):
        """Update table timers every second with precise timing"""
        print("⏰ Precise table timer system started")
        while self.running:
            try:
                current_time = datetime.now()
                
                for tables in [self.snooker_tables, self.pool_tables]:
                    for table_id, table in tables.items():
                        if table['status'] == 'running' and table['last_update']:
                            # Calculate precise time difference
                            time_diff = (current_time - table['last_update']).total_seconds()
                            table['elapsed_seconds'] += int(time_diff)
                            table['last_update'] = current_time
                            
                            # Update display time
                            minutes = table['elapsed_seconds'] // 60
                            seconds = table['elapsed_seconds'] % 60
                            table['time'] = f"{minutes:02d}:{seconds:02d}"
                            
                            # Update amount
                            duration_minutes = table['elapsed_seconds'] / 60
                            table['amount'] = duration_minutes * table['rate']
                
                # Sleep for exactly 1 second
                time.sleep(1.0)
                
            except Exception as e:
                print(f"⚠️ Timer error: {e}")
                time.sleep(1.0)
    
    def stop(self):
        """Stop the timer system"""
        self.running = False
        print("⏰ Table timer system stopped")
