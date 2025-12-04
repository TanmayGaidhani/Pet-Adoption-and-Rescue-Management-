from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['rescue_pet']
users_collection = db['users']

class User:
    """User model using PyMongo directly"""
    
    @staticmethod
    def create(fullname, email, phone, password):
        """Create a new user"""
        user_data = {
            'fullname': fullname,
            'email': email,
            'phone': phone,
            'password': password,
            'created_at': datetime.now()
        }
        result = users_collection.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return users_collection.find_one({'email': email})
    
    @staticmethod
    def exists(email):
        """Check if user exists"""
        return users_collection.find_one({'email': email}) is not None
