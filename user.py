import bcrypt
from db import Neo4jConnection

class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.current_user = None
        
    def register_user(self, name, email, username, password):
        """UC-1: Register a new user"""
        query = """
        MATCH (u:User {screen_name: $username})
        RETURN u
        """
        result = self.db.execute_query(query, {"username": username})
        
        if result:
            return False, "Username already exists!"
            
        #Hash pw
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        #create user node
        query = """
        CREATE (u:User {
            name: $name,
            screen_name: $username,
            email: $email,
            password: $password,
            bio: "",
            followers_count: 0,
            friends_count: 0
        })
        RETURN u
        """
        
        params = {
            "name": name,
            "username": username,
            "email": email,
            "password": hashed_password
        }
        
        result = self.db.execute_query(query, params)
        return True, "User registered successfully!"
    
    def login_user(self, username, password):
        """UC-2: User login"""
        query = """
        MATCH (u:User {screen_name: $username})
        RETURN u
        """
        result = self.db.execute_query(query, {"username": username})
        
        if not result:
            return False, "User not found!"
            
        user = result[0]['u']
        
        # For testing/demo purposes, if using the Twitter dataset which doesn't have passwords:
        # Just check if the username exists and log them in
        if 'password' not in user:
            self.current_user = user
            return True, f"Welcome back, {username}!"
            
        #Otherwise, verify password with bcrypt
        stored_password = user['password']
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            self.current_user = user
            return True, f"Welcome back, {username}!"
        else:
            return False, "Invalid password!"
            