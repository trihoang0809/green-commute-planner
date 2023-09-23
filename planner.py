from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def userAuthorization():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def getWeekLocations(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        later = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'
        print('Getting all events from now to 7 days later...')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=later, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the locations of the events for the week
        locations = []
        for event in events:
            # start = event['start'].get('dateTime', event['start'].get('date'))
            # print(start, event['location'])
            locations.append(event['location'])
        return locations
        
    except HttpError as error:
        print('An error occurred: %s' % error)
    
def main():
    # Authorize the user in order to pull their data for Google Calendar API.
    creds = userAuthorization()
    
    # Get all locations in Google Calendar for until the next week from now.
    weekLocations = getWeekLocations(creds)
    print(weekLocations)



if __name__ == '__main__':
    main()