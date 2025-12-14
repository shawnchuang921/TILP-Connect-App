# views/dashboard.py (UPDATED)
import streamlit as st
import plotly.express as px
import pandas as pd
from database import get_data # Simple import works since database.py is now in 'views'
import os 

def show_page():
    # Retrieve the child filter from the session state (set in app.py during login)
    child_filter = st.session_state.get("child_link", "All")
    user_role = st.session_state.get("user_role", "guest")

    # --- Header and Data Fetching ---
    if user_role == "parent":
        st.header(f"🏡 My Child's Progress: {child_filter}")
        st.info("This dashboard displays progress data collected by our staff for your child only.")
    else:
        st.header("📊 Clinical Dashboard & Reports")
        st.info("Review program-wide progress or filter by individual child.")
        
    try:
        df = get_data("progress")
    except Exception as e:
        st.error(f"Error loading progress data. Error: {e}")
        return

    if df.empty:
        st.warning("No progress data recorded yet. Go to 'Progress Tracker' to add entries.")
        return

    # --- Filtering Logic ---
    if child_filter != "All":
        # Parent View: Filter data for their specific child
        df_display = df[df["child_name"] == child_filter].copy()
        if df_display.empty:
            st.warning(f"No progress data found for {child_filter}.")
            return
        selected_child = child_filter
    else:
        # Staff/Admin View: Selectbox Filter
        df_display = df.copy() 
        with st.expander("🔎 Filter Data", expanded=True):
            child_list = ["All Children"] + sorted(df_display["child_name"].unique().tolist())
            selected_child = st.selectbox("Select Child", child_list)
        
        if selected_child != "All Children":
            df_display = df_display[df_display["child_name"] == selected_child]
            
        if df_display.empty:
            st.warning(f"No progress data found for the selection: {selected_child}.")
            return

    # --- Display Metrics and Charts ---
    
    st.divider()
    
    if selected_child == "All Children":
        st.subheader("Program-Wide Metrics")
    else:
        st.subheader(f"Key Progress Metrics for {selected_child}")
        
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Total Sessions Logged", len(df_display))
    progress_count = len(df_display[df_display["status"] == "Progress"])
    success_rate = round((progress_count / len(df_display)) * 100) if len(df_display) > 0 else 0
    m2.metric("Positive Progress Rate", f"{success_rate}%")
    latest_status = df_display.sort_values(by="date", ascending=False).iloc[0]["status"] if not df_display.empty else "N/A"
    m3.metric("Latest Recorded Status", latest_status)

    # CHARTS
    st.divider()
    
    st.subheader(f"Goal Achievement Trend")
    
    status_map = {"Regression": 1, "Stable": 2, "Progress": 3}
    # Use .loc to avoid SettingWithCopyWarning
    df_display.loc[:, "numeric_status"] = df_display["status"].map(status_map)
    
    fig = px.line(df_display, x="date", y="numeric_status", color="goal_area",
                  title="Status of Goals Over Time (1=Regression, 3=Progress)",
                  markers=True)
    
    fig.update_layout(yaxis=dict(
        tickvals=[1, 2, 3],
        ticktext=["Regression", "Stable", "Progress"],
        title="Performance Status"
    ))
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Recent Notes and Media Display ---
    st.subheader("Recent Notes & Media")
    
    # Iterate through the filtered data and display notes/media
    for index, row in df_display.sort_values(by="date", ascending=False).head(50).iterrows():
        st.markdown(f"**{row['date']}** | **{row['discipline']}** | **Goal:** {row['goal_area']} | **Status:** **{row['status']}**")
        st.markdown(f"**Notes:** {row['notes']}")
        
        if pd.notna(row['media_path']) and row['media_path'] and os.path.exists(row['media_path']):
            file_path = row['media_path']
            # Get the file extension to determine the type
            mime_type = os.path.splitext(file_path)[1].lower()
            
            with st.expander(f"View Attached Media ({os.path.basename(file_path)})"):
                if mime_type in ['.jpg', '.jpeg', '.png']:
                    st.image(file_path, caption="Therapist Media", use_column_width=True)
                elif mime_type in ['.mp4', '.mov']:
                    st.video(file_path, format="video/mp4")
                else:
                    st.warning(f"Media found but cannot display: {os.path.basename(file_path)}")
            
        st.markdown("---")
