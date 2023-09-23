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

def run():    
    st.set_page_config(
        page_title="Green Commute",
        page_icon="🛴",
    )

    st.write("# Green Commute Planner")
    
    print("HELLO")

    if st.button("Log in", type="primary"):
        creds = auth.userAuthorization()
        print("HELLO")
        return creds
    
def main():
    # Set up config for website? (Authenticate the user in order to pull their data for Google Calendar API.)
    creds = run()

    # Get all locations in Google Calendar for until the next week from now.
    weekLocations = calendarDataRetriever.getWeekLocations(creds)
    print(weekLocations)
    
    # Get all paths for the week and calculate the path distance.
    pathDistances = []
    for i in range(len(weekLocations)-1):
        fromLoc, toLoc = weekLocations[i], weekLocations[i+1]
        dist = maps.getPathDistance(fromLoc, toLoc)
        pathDistances.append((toLoc[1], fromLoc[0], toLoc[0], dist)) # (toStartTime, fromEventName, toEventName, dist)
        
    # Display path distances on site.
    display_events(pathDistances)

    transportation = st.selectbox(
    'Which method of transportation do you log?',
    ('Walk', 'Bike', 'Bus/Train', 'Car', 'Plane'), placeholder="Choose an Option")
    if st.button("Log", type="primary"):
        # Do something else
        st.write(transportation)

def display_events(pathDistances):  # [(toStartTime, fromEventName, toEventName, dist)]
    if not pathDistances:
        st.write("No upcoming events found.")
        return
    # Loop through events and display them
    for path in pathDistances: # loc is of form (eventName, UTCTime, location)
        st.write(f"**Time When User Finishes Path:** {path[0]}")
        st.write(f"**Starting Location:** {path[1]}")
        st.write(f"**Ending Location:** {path[2]}")
        st.write(f"**Path Distance:** {path[3]}")
        st.write("---")

if __name__ == '__main__':
    # Check if 'started' key exists in session_state, if not, run main.
    if not st.session_state.get('started'):
        main()
