# views/tracker.py (UPDATED)
import streamlit as st
from database import save_progress, get_list_data
from datetime import date
import os
import uuid # For creating unique filenames

def show_page():
    st.header("📝 Client Progress Tracker")
    st.info("Log daily outcomes for clients here. This feeds the Dashboard.")

    # --- DYNAMIC LISTS ---
    try:
        children = get_list_data("children")["child_name"].tolist()
        disciplines = get_list_data("disciplines")["name"].tolist()
        goal_areas = get_list_data("goal_areas")["name"].tolist()
    except Exception as e:
        st.error(f"Error loading lists from database. Check 'Admin Tools' and 'database.py'. Error: {e}")
        return

    if not children:
        st.warning("No children found. Please add children in 'Admin Tools' first.")
        return

    # Form to prevent reloading on every click
    with st.form("progress_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_input = st.date_input("Date", date.today())
            child = st.selectbox("Child Name", children)
            discipline = st.selectbox("Discipline", disciplines)
        
        with col2:
            goal_area = st.selectbox("Goal Area", goal_areas)
            status = st.select_slider("Performance Status", options=["Regression", "Stable", "Progress"], value="Stable")
        
        notes = st.text_area("Anecdotal Notes", placeholder="e.g., Used spoon independently for 3 scoops...")
        
        # --- MEDIA UPLOAD (Request 4) ---
        media_file = st.file_uploader("Upload Photo/Video (Optional)", 
                                      type=['jpg', 'jpeg', 'png', 'mp4', 'mov'], 
                                      help="Attach a photo or short video clip for the parent to view.")
        
        submitted = st.form_submit_button("💾 Save Entry")
        
        if submitted:
            media_path = ""
            if media_file is not None:
                # Create a unique filename and save the file to the 'media' folder
                file_extension = media_file.name.split('.')[-1]
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                media_path = os.path.join("media", unique_filename)
                
                # Write the file content to disk
                try:
                    with open(media_path, "wb") as f:
                        f.write(media_file.getbuffer())
                    st.success(f"File saved as: {media_path}")
                except Exception as e:
                    st.error(f"Could not save file: {e}")
                    media_path = "" # Clear path if save failed
            
            # Save the record to the database
            save_progress(date_input, child, discipline, goal_area, status, notes, media_path)
            st.success(f"Progress data saved for {child}!")
