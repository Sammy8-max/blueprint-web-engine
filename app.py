import streamlit as st
import pandas as pd
from io import StringIO

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

if st.button("GENERATE DATA FOR SPREADSHEET PASTE"):
    if not raw_input.strip():
        st.warning("No data detected.")
    else:
        try:
            # 1. READ & CLEAN DATA
            df = pd.read_csv(StringIO(raw_input), sep=None, engine='python')
            stat_cols = ['WINS', 'DRAWS', 'LOSSES', 'Points', 'GSCORED', 'G CONCEDED']
            for col in stat_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['WINS', 'DRAWS', 'LOSSES']).reset_index(drop=True)
            output_rows = []

            # 2. PROCESS IN 3-ROW BLOCKS (To match your bordered table)
            for i in range(0, len(df), 2):
                if i + 1 >= len(df): break
                
                h = df.iloc[i].copy()
                a = df.iloc[i+1].copy()

                # Shared Calculation Logic[cite: 1]
                fav_s, dog_s = h.get('Strength Fav'), h.get('Strength Dog')
                w_pool = h['WINS'] + a['LOSSES']
                d_pool = h['DRAWS'] + a['DRAWS']
                l_pool = h['LOSSES'] + a['WINS']
                mp_total = w_pool + d_pool + l_pool
                
                f_p, x_p, d_p = (w_pool/mp_total), (d_pool/mp_total), (l_pool/mp_total)

                # ROW 1 (HOME)[cite: 1]
                h['MP'] = (h['WINS'] + h['DRAWS'] + h['LOSSES'])
                h['Implied % Fav'], h['Implied % X'], h['Implied % dog'] = f"{f_p:.2%}", f"{x_p:.2%}", f"{d_p:.2%}"
                
                # ROW 2 (AWAY)[cite: 1]
                a['Home Team'] = "" # Blank to match your image style
                a['MP'] = (a['WINS'] + a['DRAWS'] + a['LOSSES'])
                a['Implied % Fav'], a['Implied % X'], a['Implied % dog'] = f"{f_p:.2%}", f"{x_p:.2%}", f"{d_p:.2%}"

                # ROW 3 (SUMMARY ROW)[cite: 1]
                summary = pd.Series(index=df.columns, dtype=object)
                summary['Home Team'] = ""
                summary['Match'] = ""
                summary['Strength Fav'], summary['Strength Dog'] = fav_s, dog_s
                summary['MP'] = mp_total
                summary['Implied % Fav'], summary['Implied % X'], summary['Implied % dog'] = f"{f_p:.2%}", f"{x_p:.2%}", f"{d_p:.2%}"

                output_rows.extend([h, a, summary])

            final_df = pd.DataFrame(output_rows)

            # 3. PREPARE TAB-SEPARATED OUTPUT[cite: 1]
            tsv_data = final_df.to_csv(sep='\t', index=False)
            
            st.success("✅ Calculations Complete! 3-Row structure ready.")
            st.write("### 📋 Click the copy icon and paste into Google Sheets (Cell A1):")
            st.code(tsv_data, language="text")

        except Exception as e:
            st.error(f"Processing failed: {e}")
