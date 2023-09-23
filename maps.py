import requests
import streamlit as st
import urllib.parse

def getPathDistance(fromEvent, toEvent):
    fromLocation = fromEvent
    
    # Make the HTTP request for the distance between two locations.
    http_request = "https://maps.googleapis.com/maps/api/distancematrix/json"
    http_request += "?destinations="
    http_request += urllib.parse.quote()



# cases of space, commas