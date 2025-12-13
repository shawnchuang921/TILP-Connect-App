# app.py (UPDATED)
import streamlit as st
from database import init_db
# Assuming views/tracker.py and views/dashboard.py exist in your setup
from views import tracker, planner, dashboard 

# Initialize Database
init_db()

# Page Configuration
st.set_page_config(page_title="TILP Connect", layout="wide", page_icon="🧩")

# --- ENHANCED AUTHENTICATION & PROFILES ---
# Maps login_id to (password, role, child_link)
# child_link is used for parents to filter the data they see.
USERS = {
    # Login ID    : (Password, Role, Child Name/Group)
    "adminuser": ("admin123", "admin", "All"),
    "lead_ot": ("ot123", "OT", "All"),
    "slp_staff": ("slp123", "SLP", "All"),
    "ece_lead": ("ece123", "ECE", "All"),
    "assistant": ("staff123", "Assistant", "All"),
    
    # Parent Logins - Linked to a specific child's name
    "parent_tony": ("tonypass", "parent", "Tony Smith"),
    "parent_sara": ("sarapass", "parent", "Sara Jones")
}

def login_screen():
    st.title("🔐 TILP Connect Login")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Log In"):
            if username in USERS and USERS[username][0] == password:
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = USERS[username][1] # e.g., 'admin', 'parent'
                st.session_state["child_link"] = USERS[username][2] # e.g., 'Tony Smith', 'All'
                st.session_state["username"] = username # Store the login ID
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
    username = st.session_state["username"]
    st.sidebar.title(f"👤 User: {username.capitalize()}")
    st.sidebar.markdown(f"**Role:** {user_role.upper()}")
    
    # Define available pages based on Role
    pages = {}
    
    # Staff/Therapists/Admin roles
    if user_role in ["admin", "OT", "SLP", "ECE", "Assistant"]:
        pages["📝 Progress Tracker"] = tracker.show_page
        pages["📅 Daily Planner"] = planner.show_page
    
    # Everyone (including parents) can see the dashboard
    # Note: dashboard.py will need to use st.session_state["child_link"] to filter the view for parents.
    if user_role == "parent":
        pages[f"📊 Dashboard: {st.session_state['child_link']}"] = dashboard.show_page
    else:
        pages["📊 Dashboard & Reports"] = dashboard.show_page

    selection = st.sidebar.radio("Go to:", list(pages.keys()))
    
    if st.sidebar.button("Log Out"):
        st.session_state.clear()
        st.session_state["logged_in"] = False
        st.rerun()

    # Display Selected Page
    pages[selection]()

if __name__ == "__main__":
    main()
