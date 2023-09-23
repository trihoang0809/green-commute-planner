import streamlit as st
import pandas as pd
import google.cloud.firestore
import plotly.express as px

# Initialize Firestore client
db = google.cloud.firestore.Client.from_service_account_json("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")

def plot_user_points(days_of_week, user_points):
    # Create a line plot using Plotly Express
    fig = px.line(x=days_of_week, y=user_points, markers=True)
    fig.update_layout(title='Points for each day of the week',
                      xaxis_title='Day of the Week',
                      yaxis_title='Points')
    # Display the plot using Streamlit
    st.plotly_chart(fig)

def show_leaderboard_and_user_points():
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

    # Dropdown to select a user
    usernames = [doc.id for doc in db.collection(u'users').stream()]
    selected_user = st.selectbox("Select a User", usernames)

    # Fetch points data for the selected user
    user_ref = db.collection(u'users').document(selected_user)
    user_data = user_ref.get().to_dict()
    last_7_days_points = user_data.get('last_7_days', {})

    # Prepare the data for plotting
    days_of_week = [f"Day {i}" for i in range(1, 8)]
    user_points = [last_7_days_points.get(f'day_{i}', 0) for i in range(1, 8)]

    # Display the plot using Streamlit
    plot_user_points(days_of_week, user_points)

# Streamlit app
st.title("Green Commute Leaderboard and User Points Over Time")

show_leaderboard_and_user_points()