import streamlit as st
import pandas as pd
import re
import os

st.set_page_config(layout="wide", page_title="Master Sheet Explorer & Analytics")

st.title("Master Sheet Explorer + Price Analytics 📊")

SERVER_FILE_PATH = "temp_master_sheet.xlsx"

# --- 1. PERSISTENT UPLOADER (SIDEBAR) ---
with st.sidebar:
    st.write("### 📁 Data Setup")
    
    if os.path.exists(SERVER_FILE_PATH):
        st.success("✅ File is currently loaded in server memory.")
        if st.button("🗑️ Delete Saved File & Upload New"):
            os.remove(SERVER_FILE_PATH)
            st.cache_data.clear()
            st.rerun()
            
    else:
        uploaded_file = st.file_uploader("Upload your Master Sheet (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            with open(SERVER_FILE_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("File saved securely to server! Reloading...")
            st.rerun()

# --- 2. THE SAFETY STOP (Crucial for preventing the crash!) ---
if not os.path.exists(SERVER_FILE_PATH):
    st.warning("👈 Please upload your Excel file in the sidebar to begin.")
    st.stop() # This forces Python to stop reading the rest of the file until an upload happens

# --- 3. READ & CLEAN DATA (Will only run if the file exists) ---
@st.cache_data
def load_and_clean_data(filepath):
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    return df

df = load_and_clean_data(SERVER_FILE_PATH)

# ... (The rest of your target columns and dropdown logic goes here) ...

# --- 3. REFRESH BUTTON (SIDEBAR) ---
with st.sidebar:
    st.write("### Controls")
    if st.button("🔄 Refresh Data"):
        load_data.clear()
        st.rerun()

# --- 4. TARGET COLUMNS ---
# IMPORTANT: Ensure these match your Excel headers exactly!
desc_column = "ITEM DESCRIPTION"
type_column = "TYPE NO." 

if desc_column in df.columns and type_column in df.columns:
    # Clean up column data strings (removes hidden spaces and handles blank cells safely)
    df[desc_column] = df[desc_column].astype(str).str.strip()
    df[type_column] = df[type_column].astype(str).str.strip()
    
    st.write("---")
    
    # --- 5. UNIFIED MULTI-KEYWORD SEARCH BAR ---
    search_input = st.text_input(
        "🔍 Type keywords to filter the options below (Scans both Description & Type No):", 
        value=""
    ).strip()
    
    # Start with the full list
    filtered_df = df.copy()
    
    # Smart Text Filter
    if search_input:
        keywords = search_input.split()
        for word in keywords:
            escaped_word = re.escape(word)
            pattern = rf"\b{escaped_word}\b"
            
            # Search both columns. The '|' means OR (match in Description OR Type No)
            mask_desc = filtered_df[desc_column].str.contains(pattern, regex=True, case=False, na=False)
            mask_type = filtered_df[type_column].str.contains(pattern, regex=True, case=False, na=False)
            
            filtered_df = filtered_df[mask_desc | mask_type]

    # --- 6. THE DUAL DROPDOWNS ---
    st.write("### 🎯 Refine Your Search")
    
    # Get sorted unique options based on the text filter above, adding an "Any" option
    desc_options = ["-- Any Description --"] + sorted(filtered_df[desc_column].unique())
    type_options = ["-- Any Type No --"] + sorted(filtered_df[type_column].unique())
    
    # Place dropdowns side-by-side
    col1, col2 = st.columns(2)
    with col1:
        selected_desc = st.selectbox("1. Filter by Description:", desc_options)
    with col2:
        selected_type = st.selectbox("2. Filter by Type No:", type_options)
        
    # Apply the Dropdown Filters to the Dataframe
    if selected_desc != "-- Any Description --":
        filtered_df = filtered_df[filtered_df[desc_column] == selected_desc]
        
    if selected_type != "-- Any Type No --":
        filtered_df = filtered_df[filtered_df[type_column] == selected_type]

    # --- 7. FULL SCREEN RESULTS DISPLAY ---
    st.write("---")
    
    if not filtered_df.empty:
        st.write("### Complete Details:")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Quick Stats Layout
        st.write("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="Rows Found", value=len(filtered_df))
        with m_col2:
            st.metric(label="Total Sheet Columns", value=len(filtered_df.columns))
        with m_col3:
            st.success("Dual Filter & Smart Search: Active")
            
    else:
        st.warning("No records match this combination of Description and Type No. Try resetting one to '-- Any --'.")

else:
    st.error(f"Could not find the columns '{desc_column}' and/or '{type_column}' in your Excel file.")
    st.write("### Actual column names found in your file:")
    st.write(list(df.columns))
    st.info("Check Lines 31 & 32 in your code and update the names to match the list above exactly.")
