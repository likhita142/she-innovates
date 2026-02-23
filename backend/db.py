from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    db = client["she_innovates"]
    commits_collection = db["commits"]
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("Note: The app will work without MongoDB, but commits won't be cached.")
    # Create a mock collection for development without MongoDB
    class MockCollection:
        def __init__(self):
            self._data = []
        
        def delete_many(self, query):
            self._data = [item for item in self._data if not self._matches(item, query)]
        
        def insert_many(self, items):
            self._data.extend(items)
        
        def find(self, query=None, projection=None):
            if query:
                return [item for item in self._data if self._matches(item, query)]
            return self._data
        
        def _matches(self, item, query):
            for key, value in query.items():
                if item.get(key) != value:
                    return False
            return True
    
    commits_collection = MockCollection()
