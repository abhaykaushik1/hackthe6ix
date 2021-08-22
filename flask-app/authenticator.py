import string, random, uuid, hashlib

class Authenticator:
    
    def __init__(self, driver):
        self.driver = driver
    
    def _get_hash(self, password):
        """
        return the hashed the password using a sophisticated injective algorithm
        """
        mixed_string = ""
        for i in range(len(password)):
            mixed_string += (password[i] + password[len(password) - 1 - i])

        dk = hashlib.pbkdf2_hmac('sha1', bytes(mixed_string, encoding='utf8'), b'betamanwazhere', 100000)
        return dk.hex()
    
    def register(self, email, username, password, status):
        """
        Register the user with the given email and password
        """
       # Check if username/email is not in use
        if status == "admin":
           if self.driver.find_one('admin', {'username': username}) or self.driver.find_one('admin', {'email': email}):
               return None
        elif status == "child":
            if self.driver.find_one('child', {'username': username}) or self.driver.find_one('child', {'email': email}):
                return None

        # Generate a random UUID for the user's cookie
        cookie = uuid.uuid4().hex

        # Create JSON database entry for the user
        auth_entry = {
            "cookie": cookie,
            "email": email,
            "password": self._get_hash(password),
            "status": status,
            "logged_in": False
        }
        
        if self.driver.find_one("auth", {"email": email}) is None:
            self.driver.insert_one("auth", auth_entry)
            
            if status=="admin":
                entry = {
                    'user_id': uuid.uuid4().hex,
                    'email': email,
                    'username': username,
                    'children': [],
                    'hospital': None
                }
                self.driver.insert_one("admin", entry)
            else:
                entry = {
                    'user_id': uuid.uuid4().hex,
                    'email': email,
                    'username': username,
                    'score': 0,
                    'latest-played': None,
                    'hospital': None
                }
                self.driver.insert_one("children", entry)
        
        return cookie
    
    def set_user_login_status(self, email, status):
        """
        Set the login status of the user with the given email
        """
        self.driver.update_one('auth', {"email": email}, {"$set": {"logged_in": status}})

    def get_user_login_status(self, email):
        """
        Get the login status of the user with the given email
        Returns None if user does not exist
        """
        user = self.driver.find_one('auth', {"email": email})
        if user:
            return user['logged_in']
    
    def authenticate(self, email, password):
        user = self.driver.find_one("auth", {"email": email, "password": self._get_hash(password)})
        return True if user else False