import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv

# Load .env file
# We look for .env in the parent directory of this file (myproject/myproject/ -> myproject/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://127.0.0.1:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'rescue_pet')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
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
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        from bson import ObjectId
        return users_collection.find_one({'_id': ObjectId(user_id)})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID (alias for get_by_id for consistency)"""
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return users_collection.find_one({'email': email})
    
    @staticmethod
    def update_by_id(user_id, update_data):
        """Update user by ID"""
        from bson import ObjectId
        return users_collection.update_one(
            {'_id': ObjectId(user_id)}, 
            {'$set': update_data}
        )
    
    @staticmethod
    def delete_by_id(user_id):
        """Delete user by ID"""
        from bson import ObjectId
        return users_collection.delete_one({'_id': ObjectId(user_id)})


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
    
    @staticmethod
    def count_by_user(user_id):
        """Count pet found reports by user"""
        return db['pet_found'].count_documents({'user_id': user_id})
    
    @staticmethod
    def get_recent_by_user(user_id, limit=10):
        """Get recent pet found reports by user"""
        return list(db['pet_found'].find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def delete_by_user(user_id):
        """Delete all pet found reports by user"""
        return db['pet_found'].delete_many({'user_id': user_id})


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
    
    @staticmethod
    def count_by_user(user_id):
        """Count rescue reports by user"""
        return rescues_collection.count_documents({'user_id': user_id})
    
    @staticmethod
    def get_recent_by_user(user_id, limit=10):
        """Get recent rescue reports by user"""
        return list(rescues_collection.find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def delete_by_user(user_id):
        """Delete all rescue reports by user"""
        return rescues_collection.delete_many({'user_id': user_id})


class AdoptionPet:
    """Adoption Pet model - for pets available for adoption (admin managed)"""
    
    @staticmethod
    def create(pet_data):
        """Create a new pet for adoption"""
        pet_data['created_at'] = datetime.now()
        pet_data['status'] = 'available'  # available, adopted, reserved
        result = db['adoption_pets'].insert_one(pet_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all adoption pets"""
        return list(db['adoption_pets'].find().sort('created_at', -1))
    
    @staticmethod
    def find_available():
        """Get only available pets for adoption"""
        return list(db['adoption_pets'].find({'status': 'available'}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(pet_id):
        """Find adoption pet by ID"""
        from bson import ObjectId
        return db['adoption_pets'].find_one({'_id': ObjectId(pet_id)})
    
    @staticmethod
    def update_status(pet_id, status):
        """Update pet adoption status"""
        from bson import ObjectId
        return db['adoption_pets'].update_one(
            {'_id': ObjectId(pet_id)}, 
            {'$set': {'status': status, 'updated_at': datetime.now()}}
        )
    
    @staticmethod
    def delete(pet_id):
        """Delete an adoption pet"""
        from bson import ObjectId
        return db['adoption_pets'].delete_one({'_id': ObjectId(pet_id)})


class AdoptionRequest:
    """Adoption Request model - for users requesting to adopt pets"""
    
    @staticmethod
    def create(request_data):
        """Create a new adoption request"""
        request_data['created_at'] = datetime.now()
        request_data['status'] = 'pending'  # pending, approved, rejected
        result = db['adoption_requests'].insert_one(request_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all adoption requests"""
        return list(db['adoption_requests'].find().sort('created_at', -1))
    
    @staticmethod
    def find_pending():
        """Get pending adoption requests"""
        return list(db['adoption_requests'].find({'status': 'pending'}).sort('created_at', -1))
    
    @staticmethod
    def find_by_pet_id(pet_id):
        """Find adoption requests for a specific pet"""
        return list(db['adoption_requests'].find({'pet_id': pet_id}).sort('created_at', -1))
    
    @staticmethod
    def find_by_user_id(user_id):
        """Find adoption requests by user"""
        return list(db['adoption_requests'].find({'user_id': user_id}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(request_id):
        """Find adoption request by ID"""
        from bson import ObjectId
        return db['adoption_requests'].find_one({'_id': ObjectId(request_id)})
    
    @staticmethod
    def approve(request_id):
        """Approve an adoption request"""
        from bson import ObjectId
        return db['adoption_requests'].update_one(
            {'_id': ObjectId(request_id)}, 
            {'$set': {'status': 'approved', 'approved_at': datetime.now()}}
        )
    
    @staticmethod
    def reject(request_id):
        """Reject an adoption request"""
        from bson import ObjectId
        return db['adoption_requests'].update_one(
            {'_id': ObjectId(request_id)}, 
            {'$set': {'status': 'rejected', 'rejected_at': datetime.now()}}
        )


class Comment:
    """Comment model - for user comments/messages"""
    
    @staticmethod
    def create(user_id, user_name, message):
        """Create a new comment"""
        comment_data = {
            'user_id': user_id,
            'user_name': user_name,
            'message': message,
            'created_at': datetime.now()
        }
        result = db['comments'].insert_one(comment_data)
        return result.inserted_id
    
    @staticmethod
    def find_all(limit=50):
        """Get all comments (latest first)"""
        return list(db['comments'].find().sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_by_user_id(user_id):
        """Get comments by specific user"""
        return list(db['comments'].find({'user_id': user_id}).sort('created_at', -1))
    
    @staticmethod
    def delete_by_id(comment_id):
        """Delete a comment"""
        from bson import ObjectId
        return db['comments'].delete_one({'_id': ObjectId(comment_id)})
    
    @staticmethod
    def count_total():
        """Count total comments"""
        return db['comments'].count_documents({})
    
    @staticmethod
    def count_by_user(user_id):
        """Count comments by user"""
        return db['comments'].count_documents({'user_id': user_id})
    
    @staticmethod
    def get_recent_by_user(user_id, limit=10):
        """Get recent comments by user"""
        return list(db['comments'].find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def delete_by_user(user_id):
        """Delete all comments by user"""
        return db['comments'].delete_many({'user_id': user_id})


class ChatMessage:
    """ChatMessage model - for saving chatbot conversations and pet discussions"""
    
    # Collection name for chat messages
    COLLECTION_NAME = 'pet_chat_messages'
    
    @staticmethod
    def create(message_data):
        """Create a new chat message (supports both bot chat and pet discussions)"""
        if isinstance(message_data, dict) and 'message' in message_data:
            # New format for pet discussions
            message_data['created_at'] = datetime.now()
            result = db[ChatMessage.COLLECTION_NAME].insert_one(message_data)
            return result.inserted_id
        else:
            # Legacy format for bot conversations
            user_id, user_name, user_message, bot_response = message_data
            chat_data = {
                'user_id': user_id,
                'user_name': user_name,
                'user_message': user_message,
                'bot_response': bot_response,
                'created_at': datetime.now(),
                'message_type': 'bot_conversation'
            }
            result = db[ChatMessage.COLLECTION_NAME].insert_one(chat_data)
            return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id, limit=50):
        """Get chat history for a specific user"""
        return list(db[ChatMessage.COLLECTION_NAME].find({'user_id': user_id}).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_by_report(report_id, limit=100):
        """Get chat messages for a specific pet report"""
        return list(db[ChatMessage.COLLECTION_NAME].find({
            'report_id': report_id,
            'message_type': 'pet_discussion'
        }).sort('created_at', 1).limit(limit))
    
    @staticmethod
    def find_all(limit=100):
        """Get all chat messages (for admin purposes)"""
        return list(db[ChatMessage.COLLECTION_NAME].find().sort('created_at', -1).limit(limit))
    
    @staticmethod
    def delete_by_user_id(user_id):
        """Delete all chat messages for a user"""
        return db[ChatMessage.COLLECTION_NAME].delete_many({'user_id': user_id})
    
    @staticmethod
    def count_by_user_id(user_id):
        """Count chat messages for a user"""
        return db[ChatMessage.COLLECTION_NAME].count_documents({'user_id': user_id})
    
    @staticmethod
    def delete_by_user(user_id):
        """Delete all chat messages by user (alias for delete_by_user_id)"""
        return ChatMessage.delete_by_user_id(user_id)


class PetReport:
    """Unified Pet Report model - for both LOST and FOUND pets"""
    
    @staticmethod
    def create(report_data):
        """Create a new pet report (LOST or FOUND)"""
        report_data['created_at'] = datetime.now()
        report_data['status'] = 'pending'  # pending, approved, rejected
        result = db['pet_reports'].insert_one(report_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all pet reports"""
        return list(db['pet_reports'].find().sort('created_at', -1))
    
    @staticmethod
    def find_by_type(report_type):
        """Get reports by type (LOST or FOUND)"""
        return list(db['pet_reports'].find({'report_type': report_type}).sort('created_at', -1))
    
    @staticmethod
    def find_approved_by_type(report_type):
        """Get approved reports by type"""
        return list(db['pet_reports'].find({
            'report_type': report_type, 
            'status': 'approved'
        }).sort('created_at', -1))
    
    @staticmethod
    def find_pending():
        """Get all pending reports for admin"""
        return list(db['pet_reports'].find({'status': 'pending'}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(report_id):
        """Find report by ID"""
        from bson import ObjectId
        return db['pet_reports'].find_one({'_id': ObjectId(report_id)})
    
    @staticmethod
    def approve(report_id):
        """Approve a report"""
        from bson import ObjectId
        return db['pet_reports'].update_one(
            {'_id': ObjectId(report_id)}, 
            {'$set': {'status': 'approved', 'approved_at': datetime.now()}}
        )
    
    @staticmethod
    def reject(report_id):
        """Reject a report (mark as rejected instead of deleting)"""
        from bson import ObjectId
        return db['pet_reports'].update_one(
            {'_id': ObjectId(report_id)}, 
            {'$set': {'status': 'rejected', 'rejected_at': datetime.now()}}
        )
    
    @staticmethod
    def delete_by_user(user_id):
        """Delete all reports by user"""
        return db['pet_reports'].delete_many({'user_id': user_id})
    
    @staticmethod
    def delete_by_id(report_id):
        """Delete a specific report by ID"""
        from bson import ObjectId
        return db['pet_reports'].delete_one({'_id': ObjectId(report_id)})
    
    @staticmethod
    def count_by_user(user_id):
        """Count reports by user"""
        return db['pet_reports'].count_documents({'user_id': user_id})
    
    @staticmethod
    def get_recent_by_user(user_id, limit=10):
        """Get recent reports by user"""
        return list(db['pet_reports'].find({'user_id': user_id}).sort('created_at', -1).limit(limit))


class MatchResult:
    """ML Match Result model - stores admin ML matching results"""
    
    @staticmethod
    def create(match_data):
        """Create a new match result"""
        match_data['created_at'] = datetime.now()
        match_data['status'] = 'pending'  # pending, approved, rejected
        result = db['match_results'].insert_one(match_data)
        return result.inserted_id
    
    @staticmethod
    def find_all():
        """Get all match results"""
        return list(db['match_results'].find().sort('created_at', -1))
    
    @staticmethod
    def find_by_status(status):
        """Get match results by status"""
        return list(db['match_results'].find({'status': status}).sort('created_at', -1))
    
    @staticmethod
    def find_by_id(match_id):
        """Find match result by ID"""
        from bson import ObjectId
        return db['match_results'].find_one({'_id': ObjectId(match_id)})
    
    @staticmethod
    def update_status(match_id, status, admin_notes=''):
        """Update match result status"""
        from bson import ObjectId
        update_data = {
            'status': status, 
            'updated_at': datetime.now()
        }
        if admin_notes:
            update_data['admin_notes'] = admin_notes
        if status == 'approved':
            update_data['approved_at'] = datetime.now()
        elif status == 'rejected':
            update_data['rejected_at'] = datetime.now()
            
        return db['match_results'].update_one(
            {'_id': ObjectId(match_id)}, 
            {'$set': update_data}
        )
    
    @staticmethod
    def find_high_probability_matches(threshold=0.8):
        """Find matches with high probability (≥ threshold)"""
        return list(db['match_results'].find({
            'probability': {'$gte': threshold},
            'status': 'pending'
        }).sort('probability', -1))


class Notification:
    """Notification model - for managing user notifications"""
    
    # Collection name for notifications
    COLLECTION_NAME = 'user_notifications'
    
    @staticmethod
    def create(notification_data):
        """Create a new notification"""
        notification_data['created_at'] = datetime.now()
        notification_data['is_read'] = False
        result = db[Notification.COLLECTION_NAME].insert_one(notification_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id, limit=50):
        """Get notifications for a specific user"""
        return list(db[Notification.COLLECTION_NAME].find(
            {'user_id': user_id}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_unread_by_user_id(user_id):
        """Get unread notifications for a specific user"""
        return list(db[Notification.COLLECTION_NAME].find({
            'user_id': user_id,
            'is_read': False
        }).sort('created_at', -1))
    
    @staticmethod
    def count_unread_by_user_id(user_id):
        """Count unread notifications for a user"""
        return db[Notification.COLLECTION_NAME].count_documents({
            'user_id': user_id,
            'is_read': False
        })
    
    @staticmethod
    def mark_as_read(notification_id):
        """Mark a specific notification as read"""
        return db[Notification.COLLECTION_NAME].update_one(
            {'_id': ObjectId(notification_id)},
            {
                '$set': {
                    'is_read': True,
                    'read_at': datetime.now()
                }
            }
        )
    
    @staticmethod
    def mark_all_as_read_by_user_id(user_id):
        """Mark all notifications as read for a user"""
        return db[Notification.COLLECTION_NAME].update_many(
            {
                'user_id': user_id,
                'is_read': False
            },
            {
                '$set': {
                    'is_read': True,
                    'read_at': datetime.now()
                }
            }
        )
    
    @staticmethod
    def delete_by_user_id(user_id):
        """Delete all notifications for a user"""
        return db[Notification.COLLECTION_NAME].delete_many({'user_id': user_id})
    
    @staticmethod
    def delete_old_notifications(days=30):
        """Delete notifications older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return db[Notification.COLLECTION_NAME].delete_many({
            'created_at': {'$lt': cutoff_date}
        })
    
    @staticmethod
    def find_by_id(notification_id):
        """Find notification by ID"""
        return db[Notification.COLLECTION_NAME].find_one({'_id': ObjectId(notification_id)})
    
    @staticmethod
    def find_by_type(user_id, notification_type, limit=10):
        """Find notifications by type for a user"""
        return list(db[Notification.COLLECTION_NAME].find({
            'user_id': user_id,
            'type': notification_type
        }).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def delete_by_id(notification_id):
        """Delete a specific notification"""
        return db[Notification.COLLECTION_NAME].delete_one({'_id': ObjectId(notification_id)})
    
    @staticmethod
    def find_all_admin_notifications(limit=100):
        """Get all notifications for admin monitoring"""
        return list(db[Notification.COLLECTION_NAME].find().sort('created_at', -1).limit(limit))
    
    @staticmethod
    def get_notification_stats():
        """Get notification statistics"""
        pipeline = [
            {
                '$group': {
                    '_id': '$type',
                    'count': {'$sum': 1},
                    'unread_count': {
                        '$sum': {'$cond': [{'$eq': ['$is_read', False]}, 1, 0]}
                    }
                }
            }
        ]
        return list(db[Notification.COLLECTION_NAME].aggregate(pipeline))


class SystemSettings:
    """SystemSettings model - for managing platform settings"""
    
    # Collection name for system settings
    COLLECTION_NAME = 'system_settings'
    
    @staticmethod
    def get_setting(key, default_value=None):
        """Get a specific setting value"""
        setting = db[SystemSettings.COLLECTION_NAME].find_one({'key': key})
        return setting['value'] if setting else default_value
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set a specific setting value"""
        setting_data = {
            'key': key,
            'value': value,
            'updated_at': datetime.now()
        }
        if description:
            setting_data['description'] = description
        
        return db[SystemSettings.COLLECTION_NAME].update_one(
            {'key': key},
            {'$set': setting_data},
            upsert=True
        )
    
    @staticmethod
    def get_all_settings():
        """Get all system settings"""
        return list(db[SystemSettings.COLLECTION_NAME].find())
    
    @staticmethod
    def delete_setting(key):
        """Delete a specific setting"""
        return db[SystemSettings.COLLECTION_NAME].delete_one({'key': key})
    
    @staticmethod
    def get_settings_by_category(category):
        """Get settings by category"""
        return list(db[SystemSettings.COLLECTION_NAME].find({
            'key': {'$regex': f'^{category}\\.'}
        }))
    
    @staticmethod
    def reset_to_defaults():
        """Reset all settings to default values"""
        default_settings = {
            'platform.name': 'RescueMate',
            'platform.version': '1.0.0',
            'platform.maintenance_mode': False,
            'email.notifications_enabled': True,
            'email.admin_email': 'admin@rescuemate.com',
            'email.smtp_server': 'smtp.gmail.com',
            'security.session_timeout': 60,
            'security.max_login_attempts': 5,
            'security.require_email_verification': True,
            'chat.enabled': True,
            'chat.max_message_length': 500,
            'chat.moderation_enabled': True,
            'upload.max_file_size': 10,
            'upload.allowed_file_types': 'jpg,jpeg,png,gif',
            'upload.image_compression': True,
            'database.auto_backup': True,
            'database.backup_frequency': 'daily'
        }
        
        # Clear existing settings
        db[SystemSettings.COLLECTION_NAME].delete_many({})
        
        # Insert default settings
        for key, value in default_settings.items():
            SystemSettings.set_setting(key, value)
        
        return len(default_settings)


class AuditLog:
    """AuditLog model - for tracking system activities"""
    
    # Collection name for audit logs
    COLLECTION_NAME = 'audit_logs'
    
    @staticmethod
    def log_action(user_id, action, details=None, ip_address=None):
        """Log a user action"""
        log_data = {
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
            'timestamp': datetime.now()
        }
        result = db[AuditLog.COLLECTION_NAME].insert_one(log_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_user_id(user_id, limit=50):
        """Get audit logs for a specific user"""
        return list(db[AuditLog.COLLECTION_NAME].find(
            {'user_id': user_id}
        ).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def find_by_action(action, limit=100):
        """Get audit logs by action type"""
        return list(db[AuditLog.COLLECTION_NAME].find(
            {'action': action}
        ).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def find_recent_logs(hours=24, limit=100):
        """Get recent audit logs"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return list(db[AuditLog.COLLECTION_NAME].find({
            'timestamp': {'$gte': cutoff_time}
        }).sort('timestamp', -1).limit(limit))
    
    @staticmethod
    def delete_old_logs(days=90):
        """Delete audit logs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return db[AuditLog.COLLECTION_NAME].delete_many({
            'timestamp': {'$lt': cutoff_date}
        })
    
    @staticmethod
    def get_action_stats(days=30):
        """Get action statistics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {'$match': {'timestamp': {'$gte': cutoff_date}}},
            {
                '$group': {
                    '_id': '$action',
                    'count': {'$sum': 1},
                    'unique_users': {'$addToSet': '$user_id'}
                }
            },
            {
                '$project': {
                    'action': '$_id',
                    'count': 1,
                    'unique_users': {'$size': '$unique_users'}
                }
            },
            {'$sort': {'count': -1}}
        ]
        return list(db[AuditLog.COLLECTION_NAME].aggregate(pipeline))