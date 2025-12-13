# dashboard.py (UPDATED)
import streamlit as st
import plotly.express as px
import pandas as pd # Ensure pandas is imported if it wasn't already
from database import get_data

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
        
    # Fetch Data from the 'progress' table
    try:
        df = get_data("progress")
    except Exception as e:
        st.error(f"Error loading progress data. Ensure the database.py file is updated: {e}")
        return

    if df.empty:
        st.warning("No progress data recorded yet. Go to 'Progress Tracker' to add entries.")
        return

    # --- Filtering Logic ---
    
    # 1. Parent View: Automatic Filter
    if child_filter != "All":
        # The parent is logged in, filter data for their specific child
        df_display = df[df["child_name"] == child_filter]
        
        if df_display.empty:
            st.warning(f"No progress data found for {child_filter}.")
            return
            
        selected_child = child_filter # The only child visible
        
    # 2. Staff/Admin View: Selectbox Filter
    else:
        df_display = df.copy() # Staff/Admin start with all data
        
        # Staff/Admin can use the expander to filter
        with st.expander("🔎 Filter Data", expanded=True):
            # The list of children should be pulled from the unique names in the data
            child_list = ["All Children"] + sorted(df_display["child_name"].unique().tolist())
            selected_child = st.selectbox("Select Child", child_list)
        
        if selected_child != "All Children":
            df_display = df_display[df_display["child_name"] == selected_child]
            
        if df_display.empty:
            st.warning(f"No progress data found for the selection: {selected_child}.")
            return

    # --- Display Metrics and Charts (using df_display) ---
    
    st.divider()
    
    # Title for the metrics
    if selected_child == "All Children":
        st.subheader("Program-Wide Metrics")
    else:
        st.subheader(f"Key Progress Metrics for {selected_child}")
        
    # METRICS
    m1, m2, m3 = st.columns(3)
    
    # Metric 1: Total Sessions
    m1.metric("Total Sessions Logged", len(df_display))
    
    # Metric 2: Progress Rate
    progress_count = len(df_display[df_display["status"] == "Progress"])
    success_rate = round((progress_count / len(df_display)) * 100) if len(df_display) > 0 else 0
    m2.metric("Positive Progress Rate", f"{success_rate}%")
    
    # Metric 3: Latest Status
    latest_status = df_display.sort_values(by="date", ascending=False).iloc[0]["status"] if not df_display.empty else "N/A"
    m3.metric("Latest Recorded Status", latest_status)

    # CHARTS
    st.divider()
    
    # Display the filtered raw data table (helpful for review)
    st.subheader("Progress Entries")
    st.dataframe(df_display.sort_values(by="date", ascending=False), use_container_width=True)
    
    # Progress Trends Chart (Requires numeric mapping)
    st.subheader(f"Goal Achievement Trend")
    
    # Create a mapping for numeric plotting (Regression=1, Stable=2, Progress=3)
    status_map = {"Regression": 1, "Stable": 2, "Progress": 3}
    # Check if the column exists before mapping (to prevent re-running if already done)
    if "numeric_status" not in df_display.columns:
        df_display["numeric_status"] = df_display["status"].map(status_map)
    
    # Line Chart
    fig = px.line(df_display, x="date", y="numeric_status", color="goal_area",
                  title="Status of Goals Over Time (1=Regression, 3=Progress)",
                  markers=True,
                  category_orders={"status": ["Regression", "Stable", "Progress"]})
    
    # Customize Y-axis to show text labels instead of numbers
    fig.update_layout(yaxis=dict(
        tickvals=[1, 2, 3],
        ticktext=["Regression", "Stable", "Progress"],
        title="Performance Status"
    ))
    
    st.plotly_chart(fig, use_container_width=True)

    # Bar Chart: Status Distribution by Goal Area
    st.subheader("Status Distribution by Goal Area")
    fig_bar = px.bar(df_display, x="goal_area", color="status",
                     category_orders={"status": ["Regression", "Stable", "Progress"]},
                     color_discrete_map={"Progress": "green", "Stable": "blue", "Regression": "red"},
                     title="Total Entries by Status and Goal Area")
    st.plotly_chart(fig_bar, use_container_width=True)
