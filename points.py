import streamlit as st
import pandas as pd
import google.cloud.firestore
import plotly.express as px
from scipy.stats import norm

# Initialize Firestore client
db = google.cloud.firestore.Client.from_service_account_json("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")
# Assume the national average carbon footprint is 2.0
national_average_carbon_footprint = 3.2

def plot_data_with_averages(days_of_week, carbon_footprint, title, yaxis_title):
    # Calculate the "user average" for carbon footprint
    user_average = sum(carbon_footprint) / len(carbon_footprint)
    user_average_list = [user_average] * len(days_of_week)
    
    # Assume a "national average" (in this case,  for all Americans' commute)
    national_average_list = [national_average_carbon_footprint] * len(days_of_week)

    # Prepare data for plotting
    plot_data = pd.DataFrame({
        'Days of Week': days_of_week,
        'User Carbon Footprint': carbon_footprint,
        'User Average': user_average_list,
        'National Average': national_average_list
    })

    # Create the plot using Plotly Express
    fig = px.line(plot_data, x='Days of Week', y=['User Carbon Footprint', 'User Average', 'National Average'])
    fig.update_layout(title=title,
                      xaxis_title='Day of the Week',
                      yaxis_title=yaxis_title)

    # Display the plot using Streamlit
    st.plotly_chart(fig)

def plot_data(days_of_week, data, title, yaxis_title):
    # Create a line plot using Plotly Express
    fig = px.line(x=days_of_week, y=data, markers=True)
    fig.update_layout(title=title,
                      xaxis_title='Day of the Week',
                      yaxis_title=yaxis_title)
    # Display the plot using Streamlit
    st.plotly_chart(fig)

# Streamlit app
st.title("Green Commute Leaderboard and User Points Over Time")

# Fetch data from Firestore
users_ref = db.collection(u'users')
docs = users_ref.stream()

data = {
    "Usernames": [],
    "Points Today": [],
    "Last 7 Days Total": []
}

# Load usernames and data for table
for doc in docs:
    doc_data = doc.to_dict()
    data["Usernames"].append(doc_data.get('username', 'N/A'))
    data["Points Today"].append(doc_data.get('points_today', 0))
    data["Last 7 Days Total"].append(sum(doc_data.get('last_7_days', {}).values()))

# Create and display a DataFrame for leaderboard
df = pd.DataFrame(data).sort_values("Points Today", ascending=False).set_index("Usernames")
st.table(df)

# Dropdown to select a user
usernames = [doc.id for doc in db.collection(u'users').stream()]
selected_user = st.selectbox("Select a User", usernames)

# Fetch data for the selected user
user_ref = db.collection(u'users').document(selected_user)
user_data = user_ref.get().to_dict()

# Prepare and plot the points data
last_7_days_points = user_data.get('last_7_days', {})
days_of_week = [f"Day {i}" for i in range(1, 8)]
user_points = [last_7_days_points.get(f'day_{i}', 0) for i in range(1, 8)]
plot_data(days_of_week, user_points, 'Points for each day of the week', 'Points')

# Prepare and plot the carbon footprint data
last_7_days_carbon_footprint = user_data.get('carbon_footprint_last_7_days', {})
carbon_footprint = [last_7_days_carbon_footprint.get(f'day_{i}', 0) for i in range(1, 8)]

# Calculate the user's average carbon footprint
user_average_carbon_footprint = sum(carbon_footprint) / len(carbon_footprint)

# Assume a mock standard deviation for the national carbon footprint
# In a real-world scenario, this would come from empirical data
standard_deviation = 1

# Calculate the percentile of the user's carbon footprint assuming a normal distribution
percentile = norm.cdf(user_average_carbon_footprint, national_average_carbon_footprint, standard_deviation)

# Convert the percentile to the percentage of Americans the user is lower or higher than
percentage_of_americans = (1 - percentile) * 100

if user_average_carbon_footprint < national_average_carbon_footprint:
    st.info(f"Great job! Your average carbon footprint is lower than approximately {percentage_of_americans:.2f}% of Americans.")
else:
    st.info(f"Your average carbon footprint is higher than approximately {percentile * 100:.2f}% of Americans. Consider adopting greener commuting options.")

plot_data_with_averages(days_of_week, carbon_footprint, 'Carbon Footprint for each day of the week', 'Carbon Footprint')