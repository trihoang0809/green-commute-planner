from __future__ import print_function

import datetime
import os.path
import calendarDataRetriever
import auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

    
def main():
    # Authenticate the user in order to pull their data for Google Calendar API.
    creds = auth.userAuthorization()
    
    # Get all locations in Google Calendar for until the next week from now.
    weekLocations = calendarDataRetriever.getWeekLocations(creds)
    print(weekLocations)



if __name__ == '__main__':
    main()