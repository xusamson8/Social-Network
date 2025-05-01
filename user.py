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