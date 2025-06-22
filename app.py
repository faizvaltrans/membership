# app.py
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import os

MEMBERS_FILE = "members.csv"
PAYMENTS_FILE = "payments.csv"
ADMINS_FILE = "admins.csv"

st.set_page_config(page_title="Membership Manager", layout="wide")

# Load admin data
def load_admins():
    if os.path.exists(ADMINS_FILE):
        return pd.read_csv(ADMINS_FILE)
    else:
        return pd.DataFrame(columns=["Username", "Password", "Emirate"])

# Load member and payment data
def load_data():
    members = pd.read_csv(MEMBERS_FILE) if os.path.exists(MEMBERS_FILE) else pd.DataFrame(columns=[
        "Member ID", "Full Name", "Initial", "Father's Name", "Emirate", "Phone", "Address", "Remarks", "Photo URL"
    ])
    payments = pd.read_csv(PAYMENTS_FILE) if os.path.exists(PAYMENTS_FILE) else pd.DataFrame(columns=[
        "Payment ID", "Member ID", "Name", "Amount", "Date", "Notes", "Month"
    ])
    return members, payments

# Save member and payment data
def save_data(members, payments):
    members.to_csv(MEMBERS_FILE, index=False)
    payments.to_csv(PAYMENTS_FILE, index=False)

# Admin login function
def login():
    st.title("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        admins = load_admins()
        matched = admins[(admins['Username'] == username) & (admins['Password'] == password)]
        if not matched.empty:
            st.session_state.username = username
            st.session_state.emirate = matched.iloc[0]['Emirate']
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# Member management

def member_section(members, payments):
    st.subheader("👥 Manage Members")
    tab1, tab2 = st.tabs(["Add/Edit Member", "Member List"])

    with tab1:
        with st.form("member_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                initial = st.text_input("Initial")
                father = st.text_input("Father's Name")
                emirate = st.session_state.emirate
                phone = st.text_input("Phone")
            with col2:
                address = st.text_area("Address")
                remarks = st.text_input("Remarks")
                photo_url = st.text_input("Photo URL (optional)")

            if st.form_submit_button("Save Member"):
                member_id = str(uuid.uuid4())[:8]
                members = pd.concat([members, pd.DataFrame([{
                    "Member ID": member_id,
                    "Full Name": full_name,
                    "Initial": initial,
                    "Father's Name": father,
                    "Emirate": emirate,
                    "Phone": phone,
                    "Address": address,
                    "Remarks": remarks,
                    "Photo URL": photo_url
                }])], ignore_index=True)
                save_data(members, payments)
                st.success(f"Member '{full_name}' added.")

    with tab2:
        search = st.text_input("🔍 Search Members")
        emirate_filter = members[members["Emirate"] == st.session_state.emirate]
        filtered = emirate_filter[emirate_filter.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else emirate_filter
        st.dataframe(filtered, use_container_width=True)

# Payment management

def payment_section(members, payments):
    st.subheader("💸 Payments")
    tab1, tab2 = st.tabs(["Add Payment", "Payment History"])

    with tab1:
        member_list = members[members['Emirate'] == st.session_state.emirate][["Member ID", "Full Name"]].astype(str)
        if not member_list.empty:
            selection = st.selectbox("Select Member", member_list.apply(lambda x: f"{x['Member ID']} - {x['Full Name']}", axis=1))
            member_id, name = selection.split(" - ", 1)
            amount = st.number_input("Amount (AED)", min_value=0.0, step=10.0)
            date = st.date_input("Date", value=datetime.now())
            month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
            notes = st.text_input("Notes (optional)")
            if st.button("Save Payment"):
                payment_id = str(uuid.uuid4())[:8]
                payments = pd.concat([payments, pd.DataFrame([{
                    "Payment ID": payment_id,
                    "Member ID": member_id,
                    "Name": name,
                    "Amount": amount,
                    "Date": date,
                    "Notes": notes,
                    "Month": month
                }])], ignore_index=True)
                save_data(members, payments)
                st.success(f"Payment saved for {name}.")
        else:
            st.info("No members available for this emirate. Add members first.")

    with tab2:
        search = st.text_input("🔍 Search Payments")
        emirate_member_ids = members[members['Emirate'] == st.session_state.emirate]['Member ID'].tolist()
        filtered = payments[payments['Member ID'].isin(emirate_member_ids)]
        if search:
            filtered = filtered[filtered.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)]
        st.dataframe(filtered, use_container_width=True)

# Main app

def main():
    if "username" not in st.session_state:
        login()
        return

    st.title(f"🧾 Membership Manager - {st.session_state.emirate}")
    members, payments = load_data()
    member_section(members, payments)
    payment_section(members, payments)

if __name__ == '__main__':
    main()
