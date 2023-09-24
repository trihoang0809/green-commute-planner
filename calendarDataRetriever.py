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
        startDates = []
        for event in events:
            startTime = event['start'].get('dateTime', event['start'].get('date'))
            startDate = event['start']['dateTime'][:10]
            print(event)
            # print(start, event['location'])
            locations.append((event['summary'], startTime, event['location'])) # (eventName, startTime, location)
            startDates.append(startDate)
        return locations, startDates
        
    except HttpError as error:
        print('An error occurred: %s' % error)