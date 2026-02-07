#!/usr/bin/env python3
"""Connect to MongoDB (from .env) and create a test collection with one document."""
from dotenv import load_dotenv
from pymongo import MongoClient, errors
import os
import sys


def main():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("MONGODB_URI not set in environment (.env).")
        sys.exit(1)

    # Optional: allow overriding DB name via env
    db_name = os.getenv("MONGO_DB_NAME", "when2meet")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # force server selection / connection test
        client.admin.command('ping')
    except errors.ServerSelectionTimeoutError as e:
        print("Could not connect to MongoDB:", e)
        sys.exit(1)

    db = client[db_name]
    col = db["test_collection"]

    # Insert a simple test document (id returned)
    result = col.insert_one({"created_by": "script", "ok": True})
    print("Inserted document id:", result.inserted_id)

    # List collections to confirm
    print("Collections in database:", db.list_collection_names())


if __name__ == "__main__":
    main()
