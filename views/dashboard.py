import streamlit as st
import plotly.express as px
from database import get_data

def show_page():
    st.header("📊 Clinical Dashboard")
    
    # Fetch Data
    df = get_data("progress")
    
    if df.empty:
        st.warning("No data recorded yet. Go to 'Progress Tracker' to add entries.")
        return

    # Filter Bar
    with st.expander("🔎 Filter Data", expanded=True):
        selected_child = st.selectbox("Select Child", df["child_name"].unique())
    
    # Filter dataframe
    child_data = df[df["child_name"] == selected_child]
    
    # METRICS
    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Sessions", len(child_data))
    
    # Calculate Progress Rate
    progress_count = len(child_data[child_data["status"] == "Progress"])
    success_rate = round((progress_count / len(child_data)) * 100) if len(child_data) > 0 else 0
    m2.metric("Success Rate", f"{success_rate}%")
    
    m3.metric("Latest Status", child_data.iloc[-1]["status"] if not child_data.empty else "N/A")

    # CHARTS
    st.subheader(f"Progress Trends: {selected_child}")
    
    # Create a mapping for numeric plotting
    status_map = {"Regression": 1, "Stable": 2, "Progress": 3}
    child_data["numeric_status"] = child_data["status"].map(status_map)
    
    # Line Chart
    fig = px.line(child_data, x="date", y="numeric_status", color="goal_area",
                  title="Goal Achievement Over Time",
                  markers=True,
                  category_orders={"status": ["Regression", "Stable", "Progress"]})
    
    # Customize Y-axis to show text instead of numbers
    fig.update_layout(yaxis=dict(tickmode='array', tickvals=[1, 2, 3], ticktext=['Regression', 'Stable', 'Progress']))
    
    st.plotly_chart(fig, use_container_width=True)

    # Recent Notes Table
    st.subheader("Recent Notes")
    st.dataframe(child_data[["date", "discipline", "goal_area", "notes"]].sort_values(by="date", ascending=False))