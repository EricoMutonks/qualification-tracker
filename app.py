# app.py

import streamlit as st
import pandas as pd
import sqlite3
import os
import openpyxl

st.set_page_config(page_title="Qualification Approval Tracker", page_icon="📚", layout="wide")

# -------------- DATABASE FUNCTIONS --------------

DB_NAME = "qualifications.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qualifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty TEXT,
            qualification TEXT,
            status TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def seed_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM qualifications')
    count = cursor.fetchone()[0]

    if count == 0:
        sample_data = [
            ("Natural Sciences", "Bachelor of Science in Computer Science (NQF Level 7 – 360 credits)", "DHET Submitted", "2024-07-10"),
            ("EMS", "Bachelor of Commerce in Accounting (NQF Level 7 – 360 credits)", "DHET Approved", "2025-03-03"),
            ("EMS", "Bachelor of Commerce in Economics (NQF Level 7 – 360 credits)", "SAQA Registration", "2025-04-10"),
            ("CHS", "Bachelor of Arts Honours in Sport and Exercise Science (NQF Level 8 – 120 credits)", "CHE Recommendation Approval", "2025-01-31"),
            ("Arts", "Master of Arts Quality Assurance (NQF Level 9 – 180 credits)", "Not Submitted", ""),
            ("Law", "Master of Laws in Human Rights Advocacy Law (NQF Level 9 – 180 credits)", "CHE Submitted", "2024-11-10"),
            ("Arts", "Doctor of Philosophy in Anthropology (NQF Level 10 – minimum 360 credits)", "SAQA Registration", "2024-11-30"),
        ]

        cursor.executemany('''
            INSERT INTO qualifications (faculty, qualification, status, date)
            VALUES (?, ?, ?, ?)
        ''', sample_data)

        conn.commit()

    conn.close()

def load_qualifications():
    conn = get_connection()
    df = pd.read_sql_query('SELECT * FROM qualifications', conn)
    conn.close()
    return df

# -------------- STYLING --------------

def highlight_row(row):
    base_style = 'color: white; font-weight: bold;'
    if row["status"] == "Not Submitted":
        return [f'{base_style} background-color: #FF4C4C' for _ in row]
    elif "Submitted" in row["status"]:
        return [f'{base_style} background-color: #FFA500' for _ in row]
    elif "Approved" in row["status"] or "Registered" in row["status"]:
        return [f'{base_style} background-color: #2E8B57' for _ in row]
    else:
        return ['' for _ in row]

# -------------- MAIN APP --------------

def main():
    initialize_database()
    seed_database()

    st.title("🎓 Qualification Approval Tracker")

    st.subheader(f"Welcome!")

    # Load data
    df = load_qualifications()

    # Toggle between View and Edit
    view_mode = st.toggle("🔀 Toggle View Mode", value=True)

    if view_mode:
        st.subheader("View Qualifications")

        # Filter
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All"] + df["status"].unique().tolist()
        )

        if status_filter != "All":
            df = df[df["status"] == status_filter]

        styled_df = df.style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True)

        # Download buttons
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name='qualifications.csv',
            mime='text/csv',
        )

    else:
        st.subheader("✏️ Edit Qualifications")

        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="edit_table"
        )

        if st.button("💾 Save Changes"):
            conn = get_connection()
            cursor = conn.cursor()
            for idx, row in edited_df.iterrows():
                cursor.execute('''
                    UPDATE qualifications
                    SET faculty=?, qualification=?, status=?, date=?
                    WHERE id=?
                ''', (row["faculty"], row["qualification"], row["status"], row["date"], row["id"]))
            conn.commit()
            conn.close()
            st.success("✅ Changes saved successfully!")

        st.subheader("🗑️ Delete a Qualification")
        delete_id = st.number_input("Enter the ID of the record to delete:", min_value=1, step=1)

        if st.button("Delete Record"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM qualifications WHERE id=?', (delete_id,))
            conn.commit()
            conn.close()
            st.success(f"✅ Record with ID {delete_id} deleted successfully!")

if __name__ == "__main__":
    main()
