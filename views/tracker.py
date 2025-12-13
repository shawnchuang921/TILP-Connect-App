import streamlit as st
from database import save_progress
from datetime import date

def show_page():
    st.header("📝 Client Progress Tracker")
    st.info("Log daily outcomes for clients here. This feeds the Dashboard.")

    # Form to prevent reloading on every click
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.date_input("Date", date.today())
            child = st.selectbox("Child Name", ["Shawn", "Tony", "Regina", "Zoe", "Leo", "Tiffany"])
            discipline = st.selectbox("Discipline", ["OT", "SLP", "BC", "ECE"])
        
        with col2:
            goal_area = st.selectbox("Goal Area", ["Regulation", "Communication", "Fine Motor", "Social Play", "Feeding"])
            status = st.select_slider("Performance Status", options=["Regression", "Stable", "Progress"], value="Stable")
        
        notes = st.text_area("Anecdotal Notes", placeholder="e.g., Used spoon independently for 3 scoops...")
        
        submitted = st.form_submit_button("💾 Save Entry")
        
        if submitted:
            save_progress(date_input, child, discipline, goal_area, status, notes)
            st.success(f"Data saved for {child}!")