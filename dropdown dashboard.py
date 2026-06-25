import streamlit as st
import pandas as pd
import re
import os # We need this new module to check the server's hard drive

# 1. FORCE FULL SCREEN WIDE LAYOUT (Must be first!)
st.set_page_config(layout="wide", page_title="Master Sheet Explorer")

st.title("Master Sheet Explorer (Persistent Web Edition)")

# The name of the file as it will be saved on the cloud server
SERVER_FILE_PATH = "temp_master_sheet.xlsx"

# --- 2. THE PERSISTENT UPLOADER (SIDEBAR) ---
with st.sidebar:
    st.write("### 📁 Data Setup")
    
    # Check if the file is ALREADY on the server
    if os.path.exists(SERVER_FILE_PATH):
        st.success("✅ File is currently loaded in server memory.")
        st.info("You can safely close this tab and come back later. The data will remain.")
        
        # Give you a way to delete it if you want to upload a newer version
        if st.button("🗑️ Delete Saved File & Upload New"):
            os.remove(SERVER_FILE_PATH)
            st.cache_data.clear() # Clear the old data from memory
            st.rerun() # Refresh the page
            
    else:
        # If the file is NOT on the server, show the uploader
        uploaded_file = st.file_uploader("Upload your Master Sheet (.xlsx)", type=["xlsx"])
        
        if uploaded_file is not None:
            # Save the uploaded file directly to the server's local storage
            with open(SERVER_FILE_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success("File saved securely to server! Reloading...")
            st.rerun() # Refresh the page to hide the uploader and show the dashboard

# --- 3. STOP APP IF NO FILE EXISTS ---
if not os.path.exists(SERVER_FILE_PATH):
    st.warning("👈 Please upload your Excel file in the sidebar to begin.")
    st.stop()

# --- 4. READ THE SAVED FILE ---
@st.cache_data
def load_data(filepath):
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    return df

df = load_data(SERVER_FILE_PATH)

# --- 5. TARGET COLUMNS ---
desc_column = "ITEM DESCRIPTION"
type_column = "TYPE NO."

if desc_column in df.columns and type_column in df.columns:
    df[desc_column] = df[desc_column].astype(str).str.strip()
    df[type_column] = df[type_column].astype(str).str.strip()
    
    st.write("---")
    
    # --- 6. UNIFIED MULTI-KEYWORD SEARCH BAR ---
    search_input = st.text_input(
        "🔍 Type keywords to filter the options below (Scans both Description & Type No):", 
        value=""
    ).strip()
    
    filtered_df = df.copy()
    
    if search_input:
        keywords = search_input.split()
        for word in keywords:
            escaped_word = re.escape(word)
            pattern = rf"\b{escaped_word}\b"
            
            mask_desc = filtered_df[desc_column].str.contains(pattern, regex=True, case=False, na=False)
            mask_type = filtered_df[type_column].str.contains(pattern, regex=True, case=False, na=False)
            
            filtered_df = filtered_df[mask_desc | mask_type]

    # --- 7. THE DUAL DROPDOWNS ---
    st.write("### 🎯 Refine Your Search")
    
    desc_options = ["-- Any Description --"] + sorted([str(x) for x in filtered_df[desc_column].unique()])
    type_options = ["-- Any Type No --"] + sorted([str(x) for x in filtered_df[type_column].unique()])
    
    col1, col2 = st.columns(2)
    with col1:
        selected_desc = st.selectbox("1. Filter by Description:", desc_options)
    with col2:
        selected_type = st.selectbox("2. Filter by Type No:", type_options)
        
    if selected_desc != "-- Any Description --":
        filtered_df = filtered_df[filtered_df[desc_column] == selected_desc]
        
    if selected_type != "-- Any Type No --":
        filtered_df = filtered_df[filtered_df[type_column] == selected_type]

    # --- 8. FULL SCREEN RESULTS DISPLAY ---
    st.write("---")
    
    if not filtered_df.empty:
        st.write("### Complete Details:")
        st.dataframe(filtered_df, use_container_width=True)
        
        st.write("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric(label="Rows Found", value=len(filtered_df))
        with m_col2:
            st.metric(label="Total Sheet Columns", value=len(filtered_df.columns))
        with m_col3:
            st.success("Persistent Server Storage Active 💾")
            
    else:
        st.warning("No records match this combination. Try resetting one to '-- Any --'.")

else:
    st.error(f"Could not find the columns '{desc_column}' and/or '{type_column}'.")
    st.write("### Actual column names found in your uploaded file:")
    st.write(list(df.columns))
