from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth
import streamlit as st
import maps
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
    st.write("# Green Commute Planner")
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
                weekLocations = calendarDataRetriever.getWeekLocations(creds)
                print("calendar will have new locations...")
                print(weekLocations)
                return weekLocations
        else:
            return calendarDataRetriever.getWeekLocations(creds)
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

    weekLocations = get_calendar_info()
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
            mode = add_row(row, pathDistances, cols)
            if mode:
                mode_selections[row] = mode  # Store the mode selection for this row

        # Add a single Log button to log all selected modes for all paths
        if st.button("Log All"):
            for row, mode in mode_selections.items():
                log_to_firestore(pathDistances[row], mode)
            st.info("All data logged.")

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

def add_row(row, pathDistances, cols):
    path = pathDistances[row]
    distance = path[4]
    
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
        st.write("\n")
    
    with cols[1]:
        options = ["Select a mode"] + [f"{mode} ({points} points)" for mode, points in points_dict.items()]
        selected_mode = st.selectbox('Mode of Transportation Used', options, key=f'mode{row}', index=0)  # index=0 sets the default value to "Select a mode"
        st.write("\n")
    
    # To handle when "Select a mode" is chosen, you can either return None or the string itself
    return None if selected_mode == "Select a mode" else selected_mode.split(' ')[0]  # Return only the mode, not the points




if __name__ == '__main__':
    main()
