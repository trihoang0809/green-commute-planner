import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Explicitly specify the path to the service account JSON file
cred = credentials.Certificate("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")

# Initialize Firebase
firebase_admin.initialize_app(cred)

# Get a Firestore client
firestore_client = firestore.client()
