import google.cloud.firestore
import random

# Initialize Firestore client
db = google.cloud.firestore.Client.from_service_account_json("greencommute-firebase-adminsdk-kcrhl-ea92e0cdba.json")

# Sample usernames
usernames = ["Alice", "Bob", "Charlie", "Dave", "Eve"]

# Initialize the Firestore 'users' collection
users_collection = db.collection('users')

# Generate sample data and add to Firestore
for username in usernames:
    # Generate points and carbon footprint for each of the last 7 days and today
    last_7_days_points = {f"day_{i}": random.randint(50, 100) for i in range(1, 8)}
    today_points = random.randint(50, 100)

    last_7_days_carbon_footprint = {f"day_{i}": round(random.uniform(1.0, 3.0), 2) for i in range(1, 8)}
    carbon_footprint_today = round(random.uniform(1.0, 3.0), 2)
    
    # Create a new document in Firestore for each user
    doc_ref = users_collection.document(username)
    doc_ref.set({
        'username': username,
        'last_7_days': last_7_days_points,
        'points_today': today_points,
        'carbon_footprint_last_7_days': last_7_days_carbon_footprint,
        'carbon_footprint_today': carbon_footprint_today
    })

print("Sample data added to Firestore")
