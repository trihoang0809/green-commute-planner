from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth
import streamlit as st
import plotly.express as px
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

    if st.button("Log in", type="primary"):
        creds = auth.userAuthorization()
        return creds
    
def main():
    # Set up config for website? (Authenticate the user in order to pull their data for Google Calendar API.)
    creds = run()

    # Get all locations in Google Calendar for until the next week from now.
    weekLocations = calendarDataRetriever.getWeekLocations(creds)
    print(weekLocations)
    
    # Display locations on website.
    display_events(weekLocations)

    transportation = st.selectbox(
    'Which method of transportation do you log?',
    ('Walk', 'Bike', 'Bus/Train', 'Car', 'Plane'), placeholder="Choose an Option")
    if st.button("Log", type="primary"):
        st.write(transportation)


def plot_user_points(days_of_week, user_points):
    # Create a line plot using Plotly Express
    fig = px.line(x=days_of_week, y=user_points, markers=True)
    fig.update_layout(title='Points for each day of the week',
                      xaxis_title='Day of the Week', yaxis_title='Points')

    # Display the plot using Streamlit
    st.plotly_chart(fig)
# Sample data
# days_of_week = ['Monday', 'Tuesday', 'Wednesday',
#                'Thursday', 'Friday', 'Saturday', 'Sunday']
#user_points = [10, 15, 20, 18, 22, 17, 14]
# Call the function to plot the chart
#plot_user_points(days_of_week, user_points)


def display_events(weekLocations):
    if not weekLocations:
        st.write("No upcoming events found.")
        return
    # Loop through events and display them
    for loc in weekLocations: # loc is of form (eventName, UTCTime, location)
        st.write(f"**Event:** {loc[0]}")
        st.write(f"**Start Time:** {loc[1]}")
        st.write(f"**Location:** {loc[2]}")
        st.write("---")

if __name__ == '__main__':
    main()
