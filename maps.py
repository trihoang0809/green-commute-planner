import requests
import streamlit as st
import urllib.parse

import os
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
print("HELLOOOO", GOOGLE_MAPS_API_KEY)

def getPathDistance(fromEvent, toEvent): # inputs are of form (eventName, startTime, location)
    fromLocation = fromEvent[2]
    toLocation = toEvent[2]
    
    # Make the HTTP request for the distance between two locations.
    http_request = "https://maps.googleapis.com/maps/api/distancematrix/json"
    http_request += "?destinations="
    http_request += urllib.parse.quote(toLocation)
    http_request += "&origins="
    http_request += urllib.parse.quote(fromLocation)
    http_request += "&units=imperial"
    http_request += "&key="
    http_request += GOOGLE_MAPS_API_KEY
    
    # Send the HTTP request to Google Maps API and store data in JSON.
    json_data = requests.get(http_request).json()
    print(json_data)
    
    # Print the distance
    st.write(fromLocation)
    st.write(toLocation)
    st.write(json_data.get("rows")[0].get("elements")[0].get("distance").get("text"))
    st.write(json_data.get("rows")[0].get("elements")[0].get("distance").get("value"))

def main():
    fromEvent = ('TEST 2', '2023-09-24T10:00:00-05:00', 'Martel College, 99 Sunset Blvd, Houston, TX 77005, USA')
    toEvent = ('HELLO WORLD', '2023-09-24T10:00:00-05:00', 'Duncan College, 1601 Rice Boulevard, Houston, TX 77005, USA')
    getPathDistance(fromEvent, toEvent)
    
if __name__ == '__main__':
    main()

