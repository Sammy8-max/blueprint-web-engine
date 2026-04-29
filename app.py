import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
import xlsxwriter

# --- WEB CONFIG ---
st.set_page_config(page_title="Blueprint Web Engine", layout="wide")

# Rainbow Styling
st.markdown("""
    <style>
    .stApp {
        border: 10px solid;
        border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Blueprint Data Engine - Web Pro")
st.subheader("Hello User. I hope you are having a superb day!")

# Paste Area
raw_input = st.text_area("Paste your match data table here:", height=300)

if st.button("GENERATE & PREPARE FOR PASTE"):
    if not raw_input.strip():
        st.warning("No data detected.")
    else:
        try:
            # 1. THE ENGINE (Calculations)[cite: 1]
            df = pd.read_csv(StringIO(raw_input), sep=None, engine='python')
            stat_cols = ['WINS', 'DRAWS', 'LOSSES', 'Points', 'GSCORED', 'G CONCEDED']
            for col in stat_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['WINS', 'DRAWS', 'LOSSES']).reset_index(drop=True)
            output_rows = []

            for i in range(0, len(df), 2):
                if i + 1 >= len(df): break
                h, a = df.iloc[i].copy(), df.iloc[i+1].copy()

                # Math Calculations[cite: 1]
                fav_s, dog_s = h.get('Strength Fav'), h.get('Strength Dog')
                w_pool, d_pool = h['WINS'] + a['LOSSES'], h['DRAWS'] + a['DRAWS']
                l_pool = h['LOSSES'] + a['WINS']
                mp_total = w_pool + d_pool + l_pool
                
                f_p, x_p, d_p = (w_pool/mp_total), (d_pool/mp_total), (l_pool/mp_total)
                eg_fav = (h['GSCORED'] + a['G CONCEDED']) / mp_total
                eg_dog = (a['GSCORED'] + h['G CONCEDED']) / mp_total

                # Formatting for the Clipboard
                h['Strength Fav'], h['Strength Dog'] = fav_s, dog_s
                h['Implied % Fav'], h['Implied % X'], h['Implied % dog'] = f"{f_p:.2%}", f"{x_p:.2%}", f"{d_p:.2%}"
                h['Exp goals Fav'], h['Exp goals dog'] = round(eg_fav, 2), round(eg_dog, 2)
                
                a['Home Team'] = ""
                a['Implied % Fav'], a['Implied % X'], a['Implied % dog'] = f"{f_p:.2%}", f"{x_p:.2%}", f"{d_p:.2%}"
                
                output_rows.extend([h, a, pd.Series(dtype=object)]) # Add a blank line between matches

            final_df = pd.DataFrame(output_rows)

            # 2. CONVERT TO TAB-SEPARATED FOR SPREADSHEETS
            tsv_data = final_df.to_csv(sep='\t', index=False)
            
            # 3. DISPLAY RESULTS & COPY ICON
            st.success("✅ Calculations Complete!")
            
            st.write("### 📋 Copy the data below and paste directly into Excel:")
            st.code(tsv_data, language="text") 
            
            # This "st.code" block has a built-in copy button in the top right corner!

        except Exception as e:
            st.error(f"Processing failed: {e}")
