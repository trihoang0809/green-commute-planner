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
        if center_button:
            creds = auth.userAuthorization()
            if creds:
                print("getting locations...")
                weekLocations = calendarDataRetriever.getWeekLocations(creds)
                print("calendar will have new locations...")
                print(weekLocations)
                return weekLocations
    with col3 :
        pass
    return None
        
def getPaths(weekLocations): # Finds the paths given event locations for the week.
    pathDistances = []
    for i in range(len(weekLocations)-1):
        fromLoc, toLoc = weekLocations[i], weekLocations[i+1]
        dist_str, dist_units = maps.getPathDistance(fromLoc, toLoc)
        pathDistances.append((toLoc[1], fromLoc[0], toLoc[0], dist_str)) # (toStartTime, fromEventName, toEventName, dist)
    return pathDistances
        

    
def main():
    site_config()

    weekLocations = get_calendar_info()
    st.write("\n")
    
    # Get all paths for the week and calculate the path distance.
    pathDistances = None
    if weekLocations:
        pathDistances = getPaths(weekLocations)
        
    # Display path distances on site.
    if pathDistances:
        cols = st.columns(2)
        for row in range(len(pathDistances)):
            add_row(row, pathDistances, cols)

def makeModeButton():
    transportation = st.selectbox(
        'Which method of transportation do you log?',
        ('Walk', 'Bike', 'Bus/Train', 'Car', 'Plane'), placeholder="Choose an Option")
    button = st.button("Log", type="primary")
    return button, transportation


def add_row(row, pathDistances, cols):  # [(toStartTime, fromEventName, toEventName, dist)]
    if not pathDistances:
        st.write("No upcoming events found.")
        return
    
    with cols[0]:
        st.write(f"**Path (Start to Finish):** {pathDistances[row][1]} -> {pathDistances[row][2]}")
        st.write(f"**Path Distance:** {pathDistances[row][3]}")
        st.write("\n")
    with cols[1]:
        st.text_input('Mode of Transportation Used', key=f'mode{row}') 
        st.write("\n")

if __name__ == '__main__':
    main()
