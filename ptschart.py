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

# Streamlit app
st.title("User Points Over Time")

# Fetch data from Firestore
users_ref = db.collection(u'users')  # Assume you have a collection named 'users'
docs = users_ref.stream()

# Dropdown to select a user
usernames = [doc.id for doc in docs]
selected_user = st.selectbox("Select a User", usernames)

# Fetch points data for the selected user
user_ref = db.collection(u'users').document(selected_user)
user_data = user_ref.get().to_dict()
last_7_days_points = user_data.get('last_7_days', {})

# Prepare the data for plotting
days_of_week = [f"Day {i}" for i in range(1, 8)]
user_points = [last_7_days_points.get(f'day_{i}', 0) for i in range(1, 8)]

# Call the function to plot the data
plot_user_points(days_of_week, user_points)
