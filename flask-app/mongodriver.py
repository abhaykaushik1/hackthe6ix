from pymongo import MongoClient
import datetime

class MongoDriver:
    
    def __init__(self):
        self.client = MongoClient("mongodb+srv://Abhay123:LolHi123@hackathon.2gytm.mongodb.net/test")
        self.db = self.client['Assistant']
        self.children_col = self.db['children']
        self.administrators_col = self.db['administrators']
        self.autentication_col = self.db['authentication']
        self.directory = {'children': self.children_col, 'admin': self.administrators_col, "auth": self.autentication_col}
    
    def find(self, table, query):
        return self.directory[table].find(query)
    
    def find_one(self, table, query):
        return self.directory[table].find_one(query)

    def insert_one(self, table, entry):
        return self.directory[table].insert_one(entry)

    def update_one(self, table, query, new_value):
        return self.directory[table].find_one_and_update(query, new_value)
    
    def get_admin(self, admin_id):
        return self.find_one("admin", {"user_id": admin_id})
    
    def get_child(self, user_id):
        return self.find_one("children", {"chlid_id": user_id})
    
    def get_child_last_played(self, user_id):
        child = self.get_child(user_id)
        return child['last-played']
    
    def get_child_latest_score(self, user_id):
        child = self.get_child(user_id)
        return child['score']
    
    def get_child_hospital(self, user_id):
        child = self.get_child(user_id)
        return child['hospital']
    
    def get_children_in_adult_care(self, admin_id):
        adult = self.get_admin(admin_id)
        return adult["children"]
    
    def get_email_with_cookie(self, cookie):
        """
        Query the database with the given cookie id to find the user's email that the cookie is associated with
        """
        user = self.authentication_col.find_one({"cookie": cookie})
        if user is not None:
            return user['email']
    
    def get_user_id_with_cookie(self, cookie):
        """
        Query the database with the given cookie id to find the user id 
        """
        email = self.get_email_with_cookie(cookie)
        if email:
            return self.authentication_col.find_one({"email": email})['user_id']
    
    def update_score(self, user_id, score):
        if not self.get_child(user_id):
            return False
        
        child = {"chlid_id": user_id}
        new_value = {"$set": {"score": score}}
        self.update_one("child", child, new_value)
        return True
    
    def update_child_in_admin_care(self, user_id, admin_id):
        if not (self.get_child(user_id) and self.get_admin(admin_id)):
            return False
        
        admin = {"user_id": admin_id}
        children = self.get_children_in_adult_care(admin_id)
        if not children:
            children = [user_id]
        else:
            children.append(user_id)
        new_value = {"$set": {"children": children}}
        self.update_one("admin", admin, new_value)
        return True
    
    def update_child_last_played(self, user_id, timestamp):
        if not self.get_child(user_id):
            return False
        
        child = {"chlid_id": user_id}
        new_value = {"$set": {"last-played": timestamp}}
        self.update_one("child", child, new_value)
        return True