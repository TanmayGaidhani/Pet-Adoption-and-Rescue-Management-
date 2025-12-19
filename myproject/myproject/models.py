from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['rescue_pet']
users_collection = db['users']
rescues_collection = db['rescues']

class User:
    """User model using PyMongo directly"""
    
    @staticmethod
    def create(fullname, email, phone, password, is_admin=False):
        """Create a new user"""
        user_data = {
            'fullname': fullname,
            'email': email,
            'phone': phone,
            'password': password,
            'is_admin': is_admin,
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
    
    @staticmethod
    def create_admin(fullname, email, phone, password):
        """Create an admin user"""
        return User.create(fullname, email, phone, password, is_admin=True)
    
    @staticmethod
    def find_all_users():
        """Get all users (for admin panel)"""
        return list(users_collection.find().sort('created_at', -1))


class PetFound:
    """Pet Found report model - for animals found by users"""
    
    @staticmethod
    def create(found_data):
        """Create a new pet found report"""
        found_data['created_at'] = datetime.now()
        found_data['status'] = 'pending'  # All reports start as pending
        result = db['pet_found'].insert_one(found_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all pet found reports"""
        return list(db['pet_found'].find().sort('created_at', -1))
    
    @staticmethod
    def find_approved():
        """Get only approved pet found reports"""
        return list(db['pet_found'].find({'status': 'approved'}).sort('created_at', -1))
    
    @staticmethod
    def find_pending():
        """Get pending pet found reports for admin"""
        return list(db['pet_found'].find({'status': 'pending'}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(found_id):
        """Find pet found report by ID"""
        from bson import ObjectId
        return db['pet_found'].find_one({'_id': ObjectId(found_id)})
    
    @staticmethod
    def approve(found_id):
        """Approve a pet found report"""
        from bson import ObjectId
        return db['pet_found'].update_one(
            {'_id': ObjectId(found_id)}, 
            {'$set': {'status': 'approved', 'approved_at': datetime.now()}}
        )
    
    @staticmethod
    def reject(found_id):
        """Reject and DELETE a pet found report"""
        from bson import ObjectId
        return db['pet_found'].delete_one({'_id': ObjectId(found_id)})


class Rescue:
    """Animal Rescue report model - for animals needing rescue"""
    
    @staticmethod
    def create(rescue_data):
        """Create a new rescue report"""
        rescue_data['created_at'] = datetime.now()
        rescue_data['status'] = 'pending'  # All reports start as pending
        result = rescues_collection.insert_one(rescue_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all rescue reports"""
        return list(rescues_collection.find().sort('created_at', -1))
    
    @staticmethod
    def find_approved():
        """Get only approved rescue reports"""
        return list(rescues_collection.find({'status': 'approved'}).sort('created_at', -1))
    
    @staticmethod
    def find_pending():
        """Get pending rescue reports for admin"""
        return list(rescues_collection.find({'status': 'pending'}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(rescue_id):
        """Find rescue by ID"""
        from bson import ObjectId
        return rescues_collection.find_one({'_id': ObjectId(rescue_id)})
    
    @staticmethod
    def approve(rescue_id):
        """Approve a rescue report"""
        from bson import ObjectId
        return rescues_collection.update_one(
            {'_id': ObjectId(rescue_id)}, 
            {'$set': {'status': 'approved', 'approved_at': datetime.now()}}
        )
    
    @staticmethod
    def reject(rescue_id):
        """Reject and DELETE a rescue report"""
        from bson import ObjectId
        return rescues_collection.delete_one({'_id': ObjectId(rescue_id)})



