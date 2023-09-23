# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def getCalendarEvents():
    creds = None
    events_list = []  # Initialize an empty list to store event details
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Get events for the next 7 days
        now = datetime.datetime.utcnow()
        end = now + datetime.timedelta(days=7)
        now_str = now.isoformat() + 'Z'
        end_str = end.isoformat() + 'Z'

        print('Getting events for the next 7 days')
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now_str,
            timeMax=end_str,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return events_list  # Return empty list if no events

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_location = event.get('location', 'Location not specified')
            event_summary = event['summary']
            
            # Append event details as a dictionary to events_list
            events_list.append({
                'start': start,
                'summary': event_summary,
                'location': event_location
            })

        return events_list  # Return list of events

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []  # Return empty list if an error occurs

def run():
    st.set_page_config(
        page_title="Green Commute",
        page_icon="🛴",
    )

    st.write("# Welcome to Streamlit! 👋")
def display_events():

    # Call the main() function to get the list of events
    events = getCalendarEvents()

    if not events:
        st.write("No upcoming events found.")
        return
    # Loop through events and display them
    for event in events:
        st.write(f"**Event:** {event['summary']}")
        st.write(f"**Start Time:** {event['start']}")
        st.write(f"**Location:** {event['location']}")
        st.write("---")


if __name__ == "__main__":
    run()
    display_events()
