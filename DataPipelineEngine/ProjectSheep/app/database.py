import os
from pymongo import MongoClient

# 1. Pull the MongoDB connection string from our container environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/pipeline_db")

# 2. Initialize a single, reusable MongoClient instance
client = MongoClient(MONGO_URI)

# 3. Reference our specific pipeline target database
db = client["environmental_pipeline_db"]

def save_pipeline_output(report: dict, clean_data: list):
    """
    Saves the operational metadata report and all validated rows 
    into separate MongoDB collections under a atomic operation sequence.
    """
    # Write the high-level audit report (how many rows read, corrupted rows, logs)
    audit_collection = db["pipeline_audit_logs"]
    audit_collection.insert_one(report)
    
    # If we have successful rows, inject them as independent records
    if clean_data:
        data_collection = db["processed_environmental_data"]
        # insert_many takes a list of Python dictionaries and builds them into individual documents
        data_collection.insert_many(clean_data)