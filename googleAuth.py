import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # Load environment variables

google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

if google_credentials_json is None:
    raise ValueError("GOOGLE_CREDENTIALS environment variable is not set!")

# Convert the environment variable string to a JSON dictionary
google_credentials = json.loads(google_credentials_json)

# Google Sheets API Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(google_credentials, scopes=scope)
client = gspread.authorize(creds)

# Google Sheet ID and Name
SHEET_ID = "1DZNPt5Er5R9XAeTreQDg-iSsPbxhqwaky9WAIJguOpg"
SHEET_NAME = "Sheet1"

# Open the Google Sheet
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Function to read user data
def get_users():
    records = sheet.get_all_values()
    if len(records) > 1:
        df = pd.DataFrame(records[1:], columns=records[0])
        return df
    else:
        return pd.DataFrame(columns=["username", "password"])

# Function to add header if missing
def ensure_headers():
    records = sheet.get_all_values()
    if not records or records[0] != ["username", "password"]:
        sheet.insert_row(["username", "password"], 1)

# Function: Signup
def signup(username, password):
    ensure_headers()
    df = get_users()
    
    if username in df["username"].values:
        return False, "Username already exists!"
    
    sheet.append_row([username, password])
    return True, "Signup successful!"

# Function: Login
def login(username, password):
    df = get_users()
    
    if "username" not in df.columns or "password" not in df.columns:
        return False, "User data not found!"
    
    if username in df["username"].values:
        stored_password = df[df["username"] == username]["password"].values[0]
        if stored_password == password:
            return True, "Login successful!"
        else:
            return False, "Incorrect password!"
    
    return False, "User not found!"

# Streamlit UI
st.title("Streamlit Authentication (Google Sheets)")
menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if menu == "Signup":
    st.subheader("Create an Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Signup"):
        success, message = signup(new_user, new_pass)
        if success:
            st.success(message)
        else:
            st.error(message)

elif menu == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        success, message = login(username, password)
        if success:
            st.success(message)
        else:
            st.error(message)
