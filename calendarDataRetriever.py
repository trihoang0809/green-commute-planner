import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
            locations.append((event['summary'], event['location'])) # (eventName, location)
        return locations
        
    except HttpError as error:
        print('An error occurred: %s' % error)