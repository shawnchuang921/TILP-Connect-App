# views/admin_tools.py (NEW FILE)
import streamlit as st
from database import get_list_data, upsert_user, delete_user, upsert_child, delete_child, upsert_list_item, delete_list_item
import pandas as pd

def show_page():
    # Only Admin should see this page, checked in app.py
    st.title("🔑 Admin Management Tools")
    st.info("Manage User Accounts, Child Profiles, and Custom List Options.")

    # Main Tabs for Organization
    tab1, tab2, tab3 = st.tabs(["👤 User Accounts", "👨‍👩‍👧‍👦 Child Profiles", "📝 Custom Lists"])

    # --- TAB 1: USER ACCOUNTS (Request 2) ---
    with tab1:
        st.header("Staff and Parent Logins")
        df_users = get_list_data("users")
        st.dataframe(df_users, use_container_width=True)

        with st.expander("➕ Add / Edit User"):
            col1, col2 = st.columns(2)
            username = col1.text_input("Username (must be unique)", key="user_name_input")
            password = col2.text_input("Password", type="password", key="user_pass_input")
            
            col3, col4 = st.columns(2)
            role = col3.selectbox("Role", ["admin", "OT", "SLP", "ECE", "Assistant", "parent"], key="user_role_select")
            
            # Child Link is only relevant for parents
            child_link = "All"
            if role == "parent":
                # Get list of unassigned children or current child
                children_df = get_list_data("children")
                available_children = ["None"] + children_df["child_name"].tolist()
                child_link = col4.selectbox("Link to Child (for Parents)", available_children, key="user_child_link")
            else:
                col4.write("Child Link: All (Staff Role)")
            
            if st.button("Save User Account", key="save_user_btn"):
                if username and password:
                    # For staff, child_link remains 'All'
                    final_child_link = child_link if role == "parent" and child_link != "None" else "All"
                    upsert_user(username, password, role, final_child_link)
                    st.success(f"User '{username}' ({role}) saved successfully.")
                    st.rerun()
                else:
                    st.error("Username and Password are required.")
            
            if st.button("Delete User", key="delete_user_btn"):
                if username:
                    delete_user(username)
                    st.warning(f"User '{username}' deleted.")
                    st.rerun()

    # --- TAB 2: CHILD PROFILES (Request 1) ---
    with tab2:
        st.header("Client Child Profiles")
        df_children = get_list_data("children")
        st.dataframe(df_children, use_container_width=True)

        with st.expander("➕ Add / Edit Child Profile"):
            col1, col2 = st.columns(2)
            child_name = col1.text_input("Child Name (ID)", key="child_name_input")
            dob = col2.date_input("Date of Birth (Optional)", key="child_dob_input")
            
            # Get list of users with role 'parent'
            parent_df = df_users[df_users["role"] == "parent"]
            parent_list = ["None/Unassigned"] + parent_df["username"].tolist()
            
            parent_link = st.selectbox("Assign Parent Login ID", parent_list, key="parent_assign_select")

            if st.button("Save Child Profile", key="save_child_btn"):
                if child_name:
                    final_parent = parent_link if parent_link != "None/Unassigned" else "None"
                    upsert_child(child_name, final_parent, dob.isoformat())
                    
                    # Update the parent's child_link in the users table
                    if final_parent != "None":
                        upsert_user(final_parent, None, "parent", child_name) # Password is not needed for update
                        st.success(f"Child '{child_name}' saved and linked to parent '{final_parent}'.")
                    else:
                         st.success(f"Child '{child_name}' saved (no parent assigned).")
                    st.rerun()
                else:
                    st.error("Child Name is required.")
                    
            if st.button("Delete Child", key="delete_child_btn"):
                if child_name:
                    delete_child(child_name)
                    st.warning(f"Child '{child_name}' deleted. Parent link removed.")
                    st.rerun()

    # --- TAB 3: CUSTOM LISTS (Request 3) ---
    with tab3:
        st.header("Manage Goal Areas and Disciplines")
        
        col_list_1, col_list_2 = st.columns(2)
        
        # Discipline Management
        with col_list_1:
            st.subheader("Disciplines")
            df_d = get_list_data("disciplines")
            st.dataframe(df_d, use_container_width=True)
            
            d_name = st.text_input("Add/Delete Discipline Name", key="d_name_input")
            
            if st.button("Add Discipline", key="add_d_btn"):
                if d_name:
                    upsert_list_item("disciplines", d_name)
                    st.success(f"Discipline '{d_name}' added.")
                    st.rerun()
            
            if st.button("Delete Discipline", key="delete_d_btn"):
                if d_name:
                    delete_list_item("disciplines", d_name)
                    st.warning(f"Discipline '{d_name}' deleted.")
                    st.rerun()

        # Goal Area Management
        with col_list_2:
            st.subheader("Goal Areas")
            df_g = get_list_data("goal_areas")
            st.dataframe(df_g, use_container_width=True)
            
            g_name = st.text_input("Add/Delete Goal Area Name", key="g_name_input")
            
            if st.button("Add Goal Area", key="add_g_btn"):
                if g_name:
                    upsert_list_item("goal_areas", g_name)
                    st.success(f"Goal Area '{g_name}' added.")
                    st.rerun()
                    
            if st.button("Delete Goal Area", key="delete_g_btn"):
                if g_name:
                    delete_list_item("goal_areas", g_name)
                    st.warning(f"Goal Area '{g_name}' deleted.")
                    st.rerun()
