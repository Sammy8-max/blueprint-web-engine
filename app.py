import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
import xlsxwriter

# --- WEB CONFIG ---
st.set_page_config(page_title="Blueprint Web Engine", layout="wide")

# Rainbow Styling for Web
st.markdown("""
    <style>
    .reportview-container {
        border: 10px solid;
        border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🚀 Blueprint Data Engine - Web Pro")
st.subheader("Hello User. I hope you are having a superb day!")

# Paste Area
raw_input = st.text_area("Paste your match data table here:", height=300)

if st.button("GENERATE BORDERED EXCEL REPORT"):
    if not raw_input.strip():
        st.warning("No data detected.")
    else:
        try:
            # 1. READ & CLEAN DATA (Your original logic)
            df = pd.read_csv(StringIO(raw_input), sep=None, engine='python')
            stat_cols = ['WINS', 'DRAWS', 'LOSSES', 'Points']
            for col in stat_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['WINS', 'DRAWS', 'LOSSES']).reset_index(drop=True)
            
            # ... [All your Match Block processing logic goes here] ...
            # (Use the same logic from your desktop version to create output_rows)[cite: 1]
            
            # 2. CREATE EXCEL IN MEMORY
            output = BytesIO()
            final_df = pd.DataFrame(output_rows) # Based on your logic
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Blueprint')
                workbook = writer.book
                worksheet = writer.sheets['Blueprint']
                
                # ... [Insert your existing styling/border logic here] ...[cite: 1]
                
            # 3. DOWNLOAD BUTTON
            st.download_button(
                label="📥 Download Your Excel Report",
                data=output.getvalue(),
                file_name="Blueprint_Web_Report.xlsx",
                mime="application/vnd.ms-excel"
            )
            st.success(f"Successfully processed {len(df)//2} matches!")

        except Exception as e:
            st.error(f"Processing failed: {e}")