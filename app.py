import streamlit as st
from database import init_db
from views import tracker, planner, dashboard

# Initialize Database
init_db()

# Page Configuration
st.set_page_config(page_title="TILP Connect", layout="wide", page_icon="🧩")

# --- SIMPLE AUTHENTICATION ---
# In a real app, use 'streamlit-authenticator' for secure hashing.
USERS = {
    "admin": "admin123",  # Can see everything
    "staff": "staff123",  # Can edit tracker/plans
    "parent": "parent123" # Can view Dashboard only
}

def login_screen():
    st.title("🔐 TILP Connect Login")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Log In"):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = username
                st.rerun()
            else:
                st.error("Incorrect username or password")

def main():
    # Check Login Status
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login_screen()
        return

    # --- SIDEBAR NAVIGATION ---
    user_role = st.session_state["user_role"]
    st.sidebar.title(f"👤 User: {user_role.capitalize()}")
    
    # Define available pages based on Role
    pages = {}
    if user_role in ["admin", "staff"]:
        pages["📝 Progress Tracker"] = tracker.show_page
        pages["📅 Daily Planner"] = planner.show_page
    
    # Everyone (including parents) can see the dashboard
    pages["📊 Dashboard & Reports"] = dashboard.show_page

    selection = st.sidebar.radio("Go to:", list(pages.keys()))
    
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Display Selected Page
    pages[selection]()

if __name__ == "__main__":
    main()