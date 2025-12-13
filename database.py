# database.py (UPDATED & COMPLETE)
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to local database file
DB_NAME = "tilp_data.db"

def init_db():
    """Creates the tables if they don't exist yet."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table: Progress Tracker (from views/tracker.py)
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        child_name TEXT,
        discipline TEXT,
        goal_area TEXT,
        status TEXT,
        notes TEXT
    )''')
    
    # Table: Session Plans (from views/planner.py - based on Daily Session Plan.csv)
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
    
    conn.commit()
    conn.close()

def save_progress(date, child, discipline, goal, status, notes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO progress (date, child_name, discipline, goal_area, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
              (date, child, discipline, goal, status, notes))
    conn.commit()
    conn.close()

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
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df