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

def main():
    creds = None
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
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_location = event.get('location', 'Location not specified')
            print(f"{start}, {event['summary']}, Location: {event_location}")

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()



if __name__ == '__main__':
    main()
