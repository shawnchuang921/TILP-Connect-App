# database.py (FIXED for media_path KeyError)
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "tilp_data.db"

def init_db():
    """Creates all necessary tables and ensures schema is up-to-date."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Table: Users (Handles Staff & Parent Logins)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT, 
        child_link TEXT
    )''')
    
    # 2. Table: Children Profiles
    c.execute('''CREATE TABLE IF NOT EXISTS children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_name TEXT UNIQUE,
        parent_username TEXT,
        date_of_birth TEXT
    )''')
    
    # 3. Table: Custom Lists (Disciplines and Goal Areas)
    c.execute('''CREATE TABLE IF NOT EXISTS disciplines (
        name TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS goal_areas (
        name TEXT UNIQUE
    )''')
    
    # 4. Table: Progress Tracker (The minimal pre-migration schema)
    # The `IF NOT EXISTS` is intentional here.
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        child_name TEXT,
        discipline TEXT,
        goal_area TEXT,
        status TEXT,
        notes TEXT
    )''')
    
    # 5. Table: Session Plans
    c.execute('''CREATE TABLE IF NOT EXISTS session_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        lead_staff TEXT,
        support_staff TEXT,
        warm_up TEXT,
        learning_block TEXT,
        regulation_break TEXT,
        social_play TEXT,
        closing_routine TEXT,
        materials_needed TEXT,
        internal_notes TEXT
    )''')

    # --- SCHEMA MIGRATION FIX: Add 'media_path' column if it is missing ---
    try:
        # Try to execute a query that would fail if 'media_path' is missing
        c.execute("SELECT media_path FROM progress LIMIT 1")
    except sqlite3.OperationalError:
        # If it fails, the column is missing, so add it.
        c.execute("ALTER TABLE progress ADD COLUMN media_path TEXT DEFAULT ''")
        conn.commit()
    
    # --- Initial Data Load (Ensures admin/lists exist) ---
    c.execute("INSERT OR IGNORE INTO users (username, password, role, child_link) VALUES (?, ?, ?, ?)",
              ("adminuser", "admin123", "admin", "All"))
    
    for d in ["OT", "SLP", "BC", "ECE", "Assistant"]:
        c.execute("INSERT OR IGNORE INTO disciplines (name) VALUES (?)", (d,))
        
    for g in ["Regulation", "Communication", "Fine Motor", "Social Play"]:
        c.execute("INSERT OR IGNORE INTO goal_areas (name) VALUES (?)", (g,))
        
    conn.commit()
    conn.close()

# --- Progress/Data Functions (These are fine, but included for completeness) ---

def get_user(username, password):
    """Retrieves user details for login."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return {"username": user[0], "password": user[1], "role": user[2], "child_link": user[3]}
    return None

def get_data(table_name):
    """Retrieves all data from a table."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def save_progress(date, child, discipline, goal, status, notes, media_path):
    """Saves progress with the new media_path column."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO progress (date, child_name, discipline, goal_area, status, notes, media_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (date.isoformat(), child, discipline, goal, status, notes, media_path))
    conn.commit()
    conn.close()
    
# ... (All other database functions can be kept as they were in the previous update) ...
