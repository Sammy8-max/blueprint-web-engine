import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
import xlsxwriter

# --- WEB CONFIG ---
st.set_page_config(page_title="Blueprint Web Engine", layout="wide")

# Rainbow Styling for Web
st.markdown("""
    <style>
    .stApp {
        border: 10px solid;
        border-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet) 1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🚀 Blueprint Data Engine - Web Pro")
st.subheader("Hello User. I hope you are having a superb day!")

# Greeting Pop-up (Simulated for Web)
if 'first_load' not in st.session_state:
    st.toast("Hello User. I hope you are having a superb day!", icon="🌈")
    st.session_state['first_load'] = True

# Paste Area
raw_input = st.text_area("Paste your match data table here:", height=300)

if st.button("GENERATE BORDERED EXCEL REPORT"):
    if not raw_input.strip():
        st.warning("No data detected.")
    else:
        try:
            # 1. READ & CLEAN DATA
            df = pd.read_csv(StringIO(raw_input), sep=None, engine='python')
            
            # Smart Shield Logic: Ensure numeric columns
            stat_cols = ['WINS', 'DRAWS', 'LOSSES', 'Points', 'GSCORED', 'G CONCEDED']
            for col in stat_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['WINS', 'DRAWS', 'LOSSES']).reset_index(drop=True)

            if 'Strength Fav' in df.columns: df['Strength Fav'] = pd.to_numeric(df['Strength Fav'], errors='coerce')
            if 'Strength Dog' in df.columns: df['Strength Dog'] = pd.to_numeric(df['Strength Dog'], errors='coerce')

            output_rows = []

            # 2. PROCESS IN MATCH BLOCKS (The logic that was missing)[cite: 1]
            for i in range(0, len(df), 2):
                if i + 1 >= len(df): break
                
                h = df.iloc[i].copy()
                a = df.iloc[i+1].copy()

                # Venue Neutral Combined Logic[cite: 1]
                fav_s, dog_s = h.get('Strength Fav'), h.get('Strength Dog')
                w_pool = h['WINS'] + a['LOSSES']
                d_pool = h['DRAWS'] + a['DRAWS']
                l_pool = h['LOSSES'] + a['WINS']
                mp_total = w_pool + d_pool + l_pool
                
                f_p, x_p, d_p = (w_pool/mp_total), (d_pool/mp_total), (l_pool/mp_total)
                eg_fav = (h['GSCORED'] + a['G CONCEDED']) / mp_total
                eg_dog = (a['GSCORED'] + h['G CONCEDED']) / mp_total

                # ROW 1 (HOME)[cite: 1]
                h['Strength Fav'], h['Strength Dog'] = fav_s, dog_s
                h['MP'] = (h['WINS'] + h['DRAWS'] + h['LOSSES'])
                h['Diff - p'] = (h['Points'] - a['Points'])
                h['Implied % Fav'], h['Implied % X'], h['Implied % dog'] = f_p, x_p, d_p
                h['Exp goals Fav'], h['Exp goals dog'] = round(eg_fav, 2), round(eg_dog, 2)

                # ROW 2 (AWAY)[cite: 1]
                a['Home Team'] = "" 
                a['Strength Fav'], a['Strength Dog'] = fav_s, dog_s
                a['MP'] = (a['WINS'] + a['DRAWS'] + a['LOSSES'])
                a['Implied % Fav'], a['Implied % X'], a['Implied % dog'] = f_p, x_p, d_p
                a['Exp goals Fav'], a['Exp goals dog'] = None, None

                # ROW 3 (SUMMARY)[cite: 1]
                summary = pd.Series(index=df.columns, dtype=object)
                summary['Home Team'] = ""
                summary['Strength Fav'], summary['Strength Dog'] = fav_s, dog_s
                summary['MP'] = mp_total
                summary['Implied % Fav'], summary['Implied % X'], summary['Implied % dog'] = f_p, x_p, d_p
                summary['Exp goals Fav'], summary['Exp goals dog'] = None, None

                output_rows.extend([h, a, summary])

            # 3. CREATE EXCEL IN MEMORY[cite: 1]
            final_df = pd.DataFrame(output_rows)
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Blueprint')
                
                workbook  = writer.book
                worksheet = writer.sheets['Blueprint']

                # Styling[cite: 1]
                header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align': 'center'})
                base_fmt = workbook.add_format({'border': 1, 'align': 'center'})
                pct_fmt = workbook.add_format({'num_format': '0.00%', 'border': 1, 'align': 'center'})
                bottom_border_fmt = workbook.add_format({'bottom': 5, 'border': 1, 'align': 'center'})
                pct_bottom_fmt = workbook.add_format({'num_format': '0.00%', 'bottom': 5, 'border': 1, 'align': 'center'})

                for col_num, value in enumerate(final_df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)

                for row_num in range(len(final_df)):
                    excel_row = row_num + 1
                    is_summary_row = (row_num + 1) % 3 == 0 
                    
                    for col_num, col_name in enumerate(final_df.columns):
                        val = final_df.iloc[row_num, col_num]
                        current_fmt = base_fmt
                        if "Implied %" in str(col_name):
                            current_fmt = pct_bottom_fmt if is_summary_row else pct_fmt
                        elif is_summary_row:
                            current_fmt = bottom_border_fmt
                        
                        if pd.isna(val):
                            worksheet.write(excel_row, col_num, "", current_fmt)
                        else:
                            worksheet.write(excel_row, col_num, val, current_fmt)

                worksheet.set_column(0, len(final_df.columns)-1, 15)

            # 4. DOWNLOAD BUTTON
            st.download_button(
                label="📥 Download Excel Report",
                data=output.getvalue(),
                file_name="Blueprint_Web_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success(f"Batch Processed! {len(df)//2} matches organized.")

        except Exception as e:
            st.error(f"Processing failed: {e}")
