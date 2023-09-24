from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth
import streamlit as st
import maps
import pandas as pd
import google.cloud.firestore
import plotly.express as px

from PIL import Image
from scipy.stats import norm
from streamlit.logger import get_logger
from collections import defaultdict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.cloud.firestore

# Emission factors per km for different modes of transportation (hypothetical)
EMISSION_FACTORS = {
    'Walk': 0.01,
    'Bike': 0.1,
    'Bus': 0.5,
    'Plane': 2.0,
    'Car': 1.0,
}

# Base points for different modes per km
BASE_POINTS_PER_KM = {
    'Walk': 10,
    'Bike': 8,
    'Bus': 6,
    'Plane': -10,  # Negative points for flying
    'Car': -5,     # Negative points for driving a car
}

LOGGER = get_logger(__name__)
db = google.cloud.firestore.Client.from_service_account_json("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")

def site_config():
    # Set up config for website? (Authenticate the user in order to pull their data for Google Calendar API.)
    st.set_page_config(
        page_title="Green Commute",
        page_icon="🛴",
    )
    st.write("<h1 style='text-align: center;'>Green Commute Planner</h1>",unsafe_allow_html=True)
    st.write("\n")

def get_calendar_info(): # Gets locations from Google Calendar API.
    needUpdatePaths = False
    # Loads in calendar data
    col1, col2, col3 = st.columns(3)
    with col1:
        pass
    with col2:
        center_button = st.button("Input your 7-day calendar", type="primary")
        creds = auth.userAuthorization()
        if center_button:
            if creds:
                print("getting locations...")
                weekLocations, startDates = calendarDataRetriever.getWeekLocations(creds)
                print("calendar will have new locations...")
                print(weekLocations)
                return weekLocations, startDates
        else:
            weekLocations, startDates = calendarDataRetriever.getWeekLocations(creds)
            return weekLocations, startDates
    with col3 :
        pass
    return None
        
def getPaths(weekLocations): # Finds the paths given event locations for the week.
    pathDistances = []
    for i in range(len(weekLocations)-1):
        fromLoc, toLoc = weekLocations[i], weekLocations[i+1]
        dist_str, dist_units = maps.getPathDistance(fromLoc, toLoc)
        pathDistances.append((toLoc[1], fromLoc[0], toLoc[0], dist_str, dist_units)) # (toStartTime, fromEventName, toEventName, dist in km, dist in Google Maps units)
    return pathDistances
        
# def pathsToModePoints(pathDistances): # gets pathDistances and maps (path) : {mode: points}
#     print("\nConverting pathDistances to map (path) : dict(mode: point) ...\n")
    
#     result_dict = {}
#     for path in pathDistances:
#         dist = path[4]
#         fromLocation = path[1]
#         toLocation = path[2]
        
#         result_dict[(fromLocation, toLocation)] = {}
#         result_dict[(fromLocation, toLocation)]["car"] = (-1 * dist // 100)
#         result_dict[(fromLocation, toLocation)]["bus"] = (1 * dist // 100)
#         result_dict[(fromLocation, toLocation)]["bike"] = (2 * dist // 100)
#         result_dict[(fromLocation, toLocation)]["walk"] = (3 * dist // 100)
    
#     return result_dict

def calculate_points(base_points_per_km, emission_factor, distance, mode):
    base_points = base_points_per_km * distance  # Base points now depend on distance
    points = int(base_points - (emission_factor * distance))

    # Ensure that Walk, Bike, and Bus always have non-negative points
    if mode in ['Walk', 'Bike', 'Bus'] and points < 0:
        points = 0  # or any other minimum value you'd like
    
    return points
 
def main():
    site_config()

    weekLocations, startDates = get_calendar_info()
    st.write("\n")
    
    # Get all paths for the week and calculate the paths' distances.
    pathDistances = None
    mode_selections = defaultdict(str)  # To store mode selections for each row

    if weekLocations:
        pathDistances = getPaths(weekLocations)
        
    # Display path distances on site.
    if pathDistances:
        cols = st.columns(2)
        for row in range(len(pathDistances)):
            mode = add_row(row, pathDistances, cols, startDates)
            if mode:
                mode_selections[row] = mode  # Store the mode selection for this row

        # Add a single Log button to log all selected modes for all paths
        if st.button("Log All"):
            for row, mode in mode_selections.items():
                log_to_firestore(pathDistances[row], mode)
            st.info("All data logged.")
    
    #implement the charts and the leaderboard
    charts_and_leaderboard()


def charts_and_leaderboard():
    image = Image.open('goldrank.png')
    st.sidebar.image(image, width=75)
    st.sidebar.write("Your points this week: 498")
    st.sidebar.write("Current rank: Gold")
    
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
    st.sidebar.title("Green Commute Leaderboard and User Points Over Time")

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
    st.sidebar.table(df)

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
        st.sidebar.info(f"Great job! Your average carbon footprint is lower than approximately {percentage_of_americans:.2f}% of Americans.")
    else:
        st.sidebar.info(f"Your average carbon footprint is higher than approximately {percentile * 100:.2f}% of Americans. Consider adopting greener commuting options.")

    plot_data_with_averages(days_of_week, carbon_footprint, 'Carbon Footprint for each day of the week', 'Carbon Footprint')

def makeModeButton():
    transportation = st.selectbox(
        'Which method of transportation do you log?',
        ('walk', 'bike', 'bus', 'car'), placeholder="Choose an Option")
    button = st.button("Log", type="primary")
    return button, transportation

def log_to_firestore(path, mode):
    # Assume you have some way of identifying the current user
    # For example, if you have set up Firebase Authentication
    # user_id = auth.get_current_user_id()
    user_id = "some_unique_user_id"  # Mock-up user ID for demonstration
    
    # Prepare data
    data = {
        "from": path[1],
        "to": path[2],
        "mode": mode,
        "timestamp": google.cloud.firestore.SERVER_TIMESTAMP  # Adds a server timestamp
    }
    
    # Reference to the current user's document
    user_ref = db.collection("users").document(user_id)
    
    # Optionally, you can check if this user document exists, and if not, create it
    # user_ref.set({"some_field": "some_value"}, merge=True)  # The 'merge=True' ensures that the document is created if it doesn't exist
    
    # Add this event data as a new document in the "events" collection inside this user's document
    user_ref.collection("events").add(data)

def add_row(row, pathDistances, cols, startDates):
    path = pathDistances[row]
    distance = path[4]
    startDate = startDates[row]
    
    if not pathDistances:
        st.write("No upcoming events found.")
        return
    
    # Calculate points for each mode of transportation
    points_dict = {
        mode: calculate_points(BASE_POINTS_PER_KM[mode], EMISSION_FACTORS[mode], distance, mode)
        for mode in EMISSION_FACTORS.keys()
    }
    
    with cols[0]:
        st.write(f"**Path (Start to Finish):** {path[1]} -> {path[2]}")
        st.write(f"**Path Distance:** {distance} km")
        st.write(f"**Start Date:** {startDate}")
        st.write("\n")
    
    with cols[1]:
        options = ["Select a mode"] + [f"{mode} ({points} points)" for mode, points in points_dict.items()]
        selected_mode = st.selectbox('Mode of Transportation Used', options, key=f'mode{row}', index=0, help="Choose your modes of transportation for this trip")  # index=0 sets the default value to "Select a mode"
        st.write("\n")
    
    # To handle when "Select a mode" is chosen, you can either return None or the string itself
    return None if selected_mode == "Select a mode" else selected_mode.split(' ')[0]  # Return only the mode, not the points




if __name__ == '__main__':
    main()
