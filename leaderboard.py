import streamlit as st
import pandas as pd
import google.cloud.firestore

# Initialize Firestore client
db = google.cloud.firestore.Client.from_service_account_json("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")

# Streamlit app
st.title("Leaderboard")

# Fetch data from Firestore
users_ref = db.collection(u'users')  # Assume you have a collection named 'users'
docs = users_ref.stream()

data = {
    "Usernames": [],
    "Points Today": [],
    "Last 7 Days Total": []
}

for doc in docs:
    doc_data = doc.to_dict()
    username = doc_data.get('username', 'N/A')
    points_today = doc_data.get('points_today', 0)
    
    # Calculate the total points for the last 7 days
    last_7_days_points = doc_data.get('last_7_days', {})
    total_last_7_days = sum(last_7_days_points.values())
    
    data["Usernames"].append(username)
    data["Points Today"].append(points_today)
    data["Last 7 Days Total"].append(total_last_7_days)

# Create a DataFrame
df = pd.DataFrame(data)

# Sort DataFrame by Points Today
df = df.sort_values("Points Today", ascending=False)

# Display the leaderboard
st.table(df)
