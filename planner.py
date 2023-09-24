from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth
import streamlit as st
import maps
from streamlit.logger import get_logger

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


LOGGER = get_logger(__name__)

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
        
def pathsToModePoints(pathDistances): # gets pathDistances and maps (path) : {mode: points}
    print("\nConverting pathDistances to map (path) : dict(mode: point) ...\n")
    
    result_dict = {}
    for path in pathDistances:
        dist = path[4]
        fromLocation = path[1]
        toLocation = path[2]
        
        result_dict[(fromLocation, toLocation)] = {}
        result_dict[(fromLocation, toLocation)]["car"] = (-1 * dist // 100)
        result_dict[(fromLocation, toLocation)]["bus"] = (1 * dist // 100)
        result_dict[(fromLocation, toLocation)]["bike"] = (2 * dist // 100)
        result_dict[(fromLocation, toLocation)]["walk"] = (3 * dist // 100)
    
    return result_dict
        
    
def main():
    site_config()

    weekLocations = get_calendar_info()
    st.write("\n")
    
    # Get all paths for the week and calculate the paths' distances.
    pathDistances = None
    if weekLocations:
        pathDistances = getPaths(weekLocations)
        
    # Display path distances on site.
    if pathDistances:
        cols = st.columns(2)
        for row in range(len(pathDistances)):
            add_row(row, pathDistances, cols)
        # Map the paths to the points for each mode
        pathsPossiblePoints = pathsToModePoints(pathDistances)
        print(pathsPossiblePoints)

def makeModeButton():
    transportation = st.selectbox(
        'Which method of transportation do you log?',
        ('walk', 'bike', 'bus', 'car'), placeholder="Choose an Option")
    button = st.button("Log", type="primary")
    return button, transportation

def add_row(row, pathDistances, cols):  # [(toStartTime, fromEventName, toEventName, distInKiloMeters, distInUnits)]
    if not pathDistances:
        st.write("No upcoming events found.")
        return
    
    with cols[0]:
        st.write(f"**Path (Start to Finish):** {pathDistances[row][1]} -> {pathDistances[row][2]}")
        st.write(f"**Path Distance:** {pathDistances[row][3]}")
        st.write("\n")
    with cols[1]:
        mode = st.selectbox('Mode of Transportation Used',("Walk", "Bike", "Bus/Train", "Plane", "Car"), key=f'mode{row}') 
        st.write("\n")
    return mode

if __name__ == '__main__':
    main()
