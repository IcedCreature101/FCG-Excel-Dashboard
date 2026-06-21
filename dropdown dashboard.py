import streamlit as st
import pandas as pd
import re

# 1. FORCE FULL SCREEN WIDE LAYOUT (Must be first!)
st.set_page_config(layout="wide", page_title="Master Sheet Explorer")

st.title("Master Sheet Explorer")

# --- 2. FILE UPLOADER (SIDEBAR) ---
with st.sidebar:
    st.write("### 📁 Data Setup")
    # This creates the drag-and-drop box
    uploaded_file = st.file_uploader("Upload your Master Sheet (.xlsx)", type=["xlsx"])
    
    st.write("---")
    

# --- 3. STOP APP IF NO FILE UPLOADED ---
if uploaded_file is None:
    st.warning("👈 Please upload your Excel file in the sidebar to load the dashboard.")
    st.stop() # This halts the code right here until a file is dropped in.

# --- 4. READ THE UPLOADED FILE ---
# We read the file directly from memory, no C:\ drive paths needed!
@st.cache_data
def load_uploaded_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    return df

df = load_uploaded_data(uploaded_file)

# --- 5. TARGET COLUMNS ---
desc_column = "ITEM DESCRIPTION"
type_column = "TYPE NO."

if desc_column in df.columns and type_column in df.columns:
    # Clean up column data strings
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
    
   # The [str(x) for x in ...] forces every item to be text before sorting, preventing TypeErrors
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
            st.success("Ready for Cloud Deployment ☁️")
            
    else:
        st.warning("No records match this combination. Try resetting one to '-- Any --'.")

else:
    st.error(f"Could not find the columns '{desc_column}' and/or '{type_column}'.")
    st.write("### Actual column names found in your uploaded file:")
    st.write(list(df.columns))
