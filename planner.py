from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth
import streamlit as st
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
    
def main():
    # Set up config for website?
    run()
        
    # Authenticate the user in order to pull their data for Google Calendar API.
    creds = auth.userAuthorization()
    
    # Get all locations in Google Calendar for until the next week from now.
    weekLocations = calendarDataRetriever.getWeekLocations(creds)
    print(weekLocations)
    
    # Display locations on website.
    display_events(weekLocations)
    

def display_events(weekLocations):
    if not weekLocations:
        st.write("No upcoming events found.")
        return
    # Loop through events and display them
    for loc in weekLocations:
        st.write(f"**Event:** {loc[0]}")
        # st.write(f"**Start Time:** {loc['start']}")
        st.write(f"**Location:** {loc[1]}")
        st.write("---")

if __name__ == '__main__':
    main()