from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# MongoDB Connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DATABASE_NAME")]
events_collection = db["events"]

@app.route('/')
def home():
    return "Must Ketchup Backend is running!"

# 1. CREATE new event
@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    
    # Generate eventId if not provided
    if 'eventId' not in data:
        import random
        import string
        data['eventId'] = 'event_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    data['createdAt'] = datetime.utcnow()
    data['updatedAt'] = datetime.utcnow()
    
    # Insert into MongoDB
    result = events_collection.insert_one(data)
    
    return jsonify({
        "success": True,
        "eventId": data['eventId'],
        "message": "Event created successfully!"
    })

# 2. GET event by ID
@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    event = events_collection.find_one({"eventId": event_id})
    
    if not event:
        return jsonify({"success": False, "error": "Event not found"}), 404
    
    return dumps(event)

# 3. UPDATE event (add participant availability)
@app.route('/api/events/<event_id>/availability', methods=['POST'])
def update_availability(event_id):
    data = request.json
    participant_name = data.get('name')
    availability = data.get('availability', [])
    
    # Find the event
    event = events_collection.find_one({"eventId": event_id})
    
    if not event:
        return jsonify({"success": False, "error": "Event not found"}), 404
    
    # Remove existing participant if updating
    participants = event.get('participants', [])
    participants = [p for p in participants if p['name'] != participant_name]
    
    # Add updated participant
    participants.append({
        "name": participant_name,
        "availability": availability
    })
    
    # Update in MongoDB
    events_collection.update_one(
        {"eventId": event_id},
        {
            "$set": {
                "participants": participants,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    return jsonify({
        "success": True,
        "message": "Availability updated!"
    })

# 4. GET all events (optional, for debugging)
@app.route('/api/events', methods=['GET'])
def get_all_events():
    events = list(events_collection.find({}))
    return dumps(events)

if __name__ == '__main__':
    app.run(debug=True, port=3000)