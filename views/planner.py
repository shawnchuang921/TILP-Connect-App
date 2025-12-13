# views/planner.py
import streamlit as st
from datetime import date
from database import save_plan # We will create this function below

def show_page():
    st.header("📅 Daily Session Plan")
    st.info("Plan the structure of the daily session. This form replaces 'Daily Session Plan.csv'.")

    # Form to capture all planning inputs from Daily Session Plan.csv
    with st.form("session_plan_form"):
        st.subheader("General Session Details")
        col1, col2 = st.columns(2)
        
        with col1:
            plan_date = st.date_input("Date of Session", date.today())
            session_lead = st.selectbox("Session Lead (ECE Lead / Therapist)", 
                                        ["ECE - Lead", "Lead OT", "SLP - Lead", "BC - Lead", "Assistant/BI"])
        
        with col2:
            # Using multiselect for support staff, as per your workflow
            support_staff = st.multiselect("Support Staff (Assistants, etc.)", 
                                           ["Assistant/BI", "Volunteer", "OT-Assistant", "SLP-Assistant", "None"])
            materials_needed = st.text_input("Materials Needed", 
                                             placeholder="e.g., Sensory bins, laminated schedule, weighted blanket")

        st.divider()
        st.subheader("Core Session Blocks")

        # Session blocks based on your spreadsheet columns
        warm_up = st.text_area("Warm-Up Activity", 
                               placeholder="e.g., 10 min obstacle course (Gross Motor focus)", 
                               height=100)
        
        learning_block = st.text_area("Learning Block (Main Activity)", 
                                      placeholder="e.g., Circle Time: Reading a story about emotions (Communication/Behavior focus)", 
                                      height=100)

        col3, col4 = st.columns(2)
        with col3:
            regulation_break = st.text_area("Regulation Break", 
                                            placeholder="e.g., 5 min in the sensory tent (Regulation focus)", 
                                            height=100)
        with col4:
            social_play = st.text_area("Small Group / Social Play", 
                                       placeholder="e.g., Turn-taking game with peer (Social Play focus)", 
                                       height=100)

        closing_routine = st.text_area("Closing Routine", 
                                       placeholder="e.g., Tidy up song & farewell", 
                                       height=50)

        internal_notes = st.text_area("Internal Notes for Staff", 
                                      placeholder="e.g., Focus specifically on Tony's visual schedule use today.", 
                                      height=70)

        submitted = st.form_submit_button("📅 Finalize Daily Plan")
        
        if submitted:
            # Convert the list of support staff into a single string for storage
            staff_list = ", ".join(support_staff)
            
            save_plan(
                plan_date.isoformat(), 
                session_lead, 
                staff_list, 
                warm_up, 
                learning_block, 
                regulation_break, 
                social_play,
                closing_routine,
                materials_needed,
                internal_notes
            )
            st.success(f"Daily Session Plan for {plan_date.isoformat()} finalized by {session_lead}!")