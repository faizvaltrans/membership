# app.py
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import os

MEMBERS_FILE = "members.csv"
PAYMENTS_FILE = "payments.csv"
ADMIN_FILE = "admin.csv"

st.set_page_config(page_title="Membership Manager", layout="wide")

# Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "admin_city" not in st.session_state:
    st.session_state.admin_city = ""

def load_data():
    members = pd.read_csv(MEMBERS_FILE) if os.path.exists(MEMBERS_FILE) else pd.DataFrame(columns=[
        "Member ID", "Full Name", "Initial", "Father's Name", "Emirate", "Phone", "Address", "Remarks", "Photo URL"
    ])
    payments = pd.read_csv(PAYMENTS_FILE) if os.path.exists(PAYMENTS_FILE) else pd.DataFrame(columns=[
        "Payment ID", "Member ID", "Name", "Amount", "Date", "Month", "Year", "Notes", "Emirate"
    ])
    admins = pd.read_csv(ADMIN_FILE) if os.path.exists(ADMIN_FILE) else pd.DataFrame(columns=["City", "Password"])
    return members, payments, admins

def save_data(members, payments):
    members.to_csv(MEMBERS_FILE, index=False)
    payments.to_csv(PAYMENTS_FILE, index=False)

def login():
    st.title("🔐 Admin Login")
    city_options = [
        "Dubai", "Sharjah", "Ajman", "Abu Dhabi", "Al Ain",
        "Northern Emirates (Ras Al Khaimah, Fujairah, Kalba, Khor Fakkan)"
    ]
    st.session_state["login_city"] = st.selectbox("Select your Emirate/City", city_options)
    password = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        admins = pd.read_csv(ADMIN_FILE) if os.path.exists(ADMIN_FILE) else pd.DataFrame()
        matched = admins[(admins["City"] == st.session_state["login_city"]) & (admins["Password"] == password)]
        if not matched.empty:
            st.session_state.logged_in = True
            st.session_state.admin_city = st.session_state["login_city"]
            st.success(f"Welcome, Admin of {st.session_state.admin_city}")
        else:
            st.error("Invalid credentials")

def member_section(members):
    st.subheader("👥 Manage Members")
    tab1, tab2 = st.tabs(["Add/Edit Member", "Member List"])
    with tab1:
        with st.form("member_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                initial = st.text_input("Initial")
                father = st.text_input("Father's Name")
                emirate = st.selectbox("Emirate", [
                    "Dubai", "Sharjah", "Ajman", "Abu Dhabi", "Al Ain",
                    "Northern Emirates (Ras Al Khaimah, Fujairah, Kalba, Khor Fakkan)"
                ])
                phone = st.text_input("Phone")
            with col2:
                address = st.text_area("Address")
                remarks = st.text_input("Remarks")
                photo_url = st.text_input("Photo URL (optional)")
            if st.form_submit_button("Save Member"):
                member_id = str(uuid.uuid4())[:8]
                new_member = pd.DataFrame([{
                    "Member ID": member_id,
                    "Full Name": full_name,
                    "Initial": initial,
                    "Father's Name": father,
                    "Emirate": emirate,
                    "Phone": phone,
                    "Address": address,
                    "Remarks": remarks,
                    "Photo URL": photo_url
                }])
                members = pd.concat([members, new_member], ignore_index=True)
                save_data(members, pd.read_csv(PAYMENTS_FILE) if os.path.exists(PAYMENTS_FILE) else pd.DataFrame())
                st.success(f"Member '{full_name}' added.")
    with tab2:
        search = st.text_input("🔍 Search Members")
        filtered = members[members.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else members
        st.dataframe(filtered, use_container_width=True)

def payment_section(members, payments):
    st.subheader("💸 Payments")
    tab1, tab2 = st.tabs(["Add Payment", "Payment History"])
    with tab1:
        filtered_members = members[members["Emirate"] == st.session_state.admin_city]
        if filtered_members.empty:
            st.warning("No members for your Emirate yet.")
            return
        member_list = filtered_members[["Member ID", "Full Name"]].astype(str)
        selection = st.selectbox("Select Member", member_list.apply(lambda x: f"{x['Member ID']} - {x['Full Name']}", axis=1))
        member_id, name = selection.split(" - ", 1)
        amount = st.number_input("Amount (AED)", min_value=0.0, step=10.0)
        date = st.date_input("Date", value=datetime.now())
        paid_month = st.selectbox("Month Paid", list(range(1, 13)), format_func=lambda x: datetime(2025, x, 1).strftime("%B"))
        paid_year = st.number_input("Year", min_value=2020, max_value=2100, value=datetime.now().year)
        notes = st.text_input("Notes (optional)")
        if st.button("Save Payment"):
            payment_id = str(uuid.uuid4())[:8]
            new_payment = pd.DataFrame([{
                "Payment ID": payment_id,
                "Member ID": member_id,
                "Name": name,
                "Amount": amount,
                "Date": date,
                "Month": paid_month,
                "Year": paid_year,
                "Notes": notes,
                "Emirate": st.session_state.admin_city
            }])
            payments = pd.concat([payments, new_payment], ignore_index=True)
            save_data(members, payments)
            st.success(f"Payment saved for {name}.")
    with tab2:
        search = st.text_input("🔍 Search Payments")
        filtered = payments[(payments["Emirate"] == st.session_state.admin_city)]
        filtered = filtered[filtered.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else filtered
        st.dataframe(filtered, use_container_width=True)

def main():
    if not st.session_state.logged_in:
        login()
        return
    st.title("🧾 Membership Manager")
    members, payments, _ = load_data()
    member_section(members)
    payment_section(members, payments)

if __name__ == '__main__':
    main()
