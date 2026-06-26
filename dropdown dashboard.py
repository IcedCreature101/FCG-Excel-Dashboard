import streamlit as st
import pandas as pd
import re

# 1. FORCE FULL SCREEN WIDE LAYOUT
st.set_page_config(layout="wide")

st.title("Master Sheet Explorer (Multi-Filter Search)")

# --- 2. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    file_path = r"C:\Users\kauzp\OneDrive\Documents\Master sheet.xlsx"
    # Using 'rb' mode to bypass the Windows Excel lock
    with open(file_path, 'rb') as f:
        df = pd.read_excel(f)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

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
        st.dataframe(
    filtered_df, 
    use_container_width=True,
    row_height=100, # Increases cell height so text can wrap to multiple lines
    column_config={
        desc_column: st.column_config.TextColumn(
            "ITEM DESCRIPTION", 
            width="large" # Forces this specific column to stretch out
        )
    }
)
        
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
