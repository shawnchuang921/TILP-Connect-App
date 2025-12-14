# database.py (UPDATED)
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "tilp_data.db"

# --- CORE DB FUNCTIONS ---

def init_db():
    """Creates all necessary tables and populates initial admin, lists, and a test child."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Table: Users (Handles Staff & Parent Logins)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT, 
        child_link TEXT -- Used for parents to see a single child, or 'All' for staff
    )''')
    
    # 2. Table: Children Profiles (Request 1)
    c.execute('''CREATE TABLE IF NOT EXISTS children (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_name TEXT UNIQUE,
        parent_username TEXT, -- Links to a user in the 'users' table
        date_of_birth TEXT
    )''')
    
    # 3. Table: Custom Lists (Disciplines and Goal Areas - Request 3)
    c.execute('''CREATE TABLE IF NOT EXISTS disciplines (
        name TEXT UNIQUE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS goal_areas (
        name TEXT UNIQUE
    )''')
    
    # 4. Table: Progress Tracker (UPDATED for media - Request 4)
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        child_name TEXT,
        discipline TEXT,
        goal_area TEXT,
        status TEXT,
        notes TEXT,
        media_path TEXT -- NEW COLUMN for file path
    )''')
    
    # --- Initial Data Load (to ensure admin/lists exist after first run) ---
    c.execute("INSERT OR IGNORE INTO users (username, password, role, child_link) VALUES (?, ?, ?, ?)",
              ("adminuser", "admin123", "admin", "All"))
    
    for d in ["OT", "SLP", "BC", "ECE", "Assistant"]:
        c.execute("INSERT OR IGNORE INTO disciplines (name) VALUES (?)", (d,))
        
    for g in ["Regulation", "Communication", "Fine Motor", "Social Play"]:
        c.execute("INSERT OR IGNORE INTO goal_areas (name) VALUES (?)", (g,))
        
    conn.commit()
    conn.close()

def get_user(username, password):
    """Retrieves user details for login."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        # Returns: (username, password, role, child_link)
        return {"username": user[0], "password": user[1], "role": user[2], "child_link": user[3]}
    return None

def get_list_data(table_name):
    """Retrieves all data from a list table (disciplines, goal_areas, children, users)."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

# --- CRUD Functions for Admin Tools (Used in admin_tools.py) ---

def upsert_user(username, password, role, child_link):
    """Inserts or updates a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("REPLACE INTO users (username, password, role, child_link) VALUES (?, ?, ?, ?)",
              (username, password, role, child_link))
    conn.commit()
    conn.close()

def delete_user(username):
    """Deletes a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

def upsert_child(child_name, parent_username, date_of_birth=None):
    """Inserts or updates a child profile."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if child exists to decide between INSERT and UPDATE
    c.execute("SELECT id FROM children WHERE child_name=?", (child_name,))
    if c.fetchone():
        c.execute("UPDATE children SET parent_username=?, date_of_birth=? WHERE child_name=?",
                  (parent_username, date_of_birth, child_name))
    else:
        c.execute("INSERT INTO children (child_name, parent_username, date_of_birth) VALUES (?, ?, ?)",
                  (child_name, parent_username, date_of_birth))
    conn.commit()
    conn.close()

def delete_child(child_name):
    """Deletes a child and removes their parent link from the users table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Find the parent username to clear the child_link
    c.execute("SELECT parent_username FROM children WHERE child_name=?", (child_name,))
    parent = c.fetchone()
    if parent:
        # 2. Unlink the parent's child_link
        c.execute("UPDATE users SET child_link='None' WHERE username=? AND child_link=?", (parent[0], child_name))
        
    # 3. Delete the child record
    c.execute("DELETE FROM children WHERE child_name=?", (child_name,))
    conn.commit()
    conn.close()

def upsert_list_item(table_name, item_name):
    """Adds a new item to a custom list (disciplines or goal_areas)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", (item_name,))
        conn.commit()
    except sqlite3.OperationalError:
        # Handle case where table_name is invalid (should be handled in calling function)
        pass
    conn.close()

def delete_list_item(table_name, item_name):
    """Deletes an item from a custom list."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name} WHERE name=?", (item_name,))
    conn.commit()
    conn.close()

# --- Existing Progress/Planner Functions (Modified for media_path) ---

def save_progress(date, child, discipline, goal, status, notes, media_path):
    """Saves progress with the new media_path column."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO progress (date, child_name, discipline, goal_area, status, notes, media_path) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (date.isoformat(), child, discipline, goal, status, notes, media_path))
    conn.commit()
    conn.close()

# save_plan function remains the same as it doesn't use new tables, 
# but it should be placed here in the final file.
def save_plan(date, lead_staff, support_staff, warm_up, learning_block, regulation_break, social_play, closing_routine, materials_needed, internal_notes):
    """Saves a new daily session plan entry."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO session_plans (date, lead_staff, support_staff, warm_up, learning_block, regulation_break, social_play, closing_routine, materials_needed, internal_notes) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (date, lead_staff, support_staff, warm_up, learning_block, regulation_break, social_play, closing_routine, materials_needed, internal_notes))
    conn.commit()
    conn.close()

def get_data(table_name):
    """Retrieves all data from a table."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df
