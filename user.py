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
        
    def view_profile(self, username=None):
        """UC-3: View user profile"""
        if username is None and self.current_user is not None:
            username = self.current_user['screen_name']
        elif username is None:
            return False, "No user specified!"
            
        query = """
        MATCH (u:User {screen_name: $username})
        RETURN u
        """
        
        result = self.db.execute_query(query, {"username": username})
        
        if not result:
            return False, "User not found!"
            
        return True, result[0]['u']
        
    def edit_profile(self, name=None, bio=None):
        """UC-4: Edit user profile"""
        if self.current_user is None:
            return False, "You must be logged in to edit your profile!"
            
        username = self.current_user['screen_name']
        
        update_fields = []
        params = {"username": username}
        
        if name:
            update_fields.append("u.name = $name")
            params["name"] = name
            
        if bio:
            update_fields.append("u.bio = $bio")
            params["bio"] = bio
            
        if not update_fields:
            return False, "No fields to update!"
            
        query = f"""
        MATCH (u:User {{screen_name: $username}})
        SET {', '.join(update_fields)}
        RETURN u
        """
        
        result = self.db.execute_query(query, params)
        self.current_user = result[0]['u']
        
        return True, "Profile updated successfully!"
        
    def follow_user(self, username_to_follow):
        """UC-5: Follow another user"""
        if self.current_user is None:
            return False, "You must be logged in to follow users!"
            
        if self.current_user['screen_name'] == username_to_follow:
            return False, "You cannot follow yourself!"
            
        # Check if user exists
        query = """
        MATCH (u:User {screen_name: $username})
        RETURN u
        """
        
        result = self.db.execute_query(query, {"username": username_to_follow})
        
        if not result:
            return False, "User not found!"
            
        # Check if already following
        query = """
        MATCH (a:User {screen_name: $current_user})-[r:FOLLOWS]->(b:User {screen_name: $username})
        RETURN r
        """
        
        params = {
            "current_user": self.current_user['screen_name'],
            "username": username_to_follow
        }
        
        result = self.db.execute_query(query, params)
        
        if result:
            return False, "You are already following this user!"
            
        # Create follow relationship
        query = """
        MATCH (a:User {screen_name: $current_user}), (b:User {screen_name: $username})
        CREATE (a)-[r:FOLLOWS]->(b)
        
        // Update follower/following counts
        SET a.friends_count = a.friends_count + 1,
            b.followers_count = b.followers_count + 1
            
        RETURN a, b
        """
        
        result = self.db.execute_query(query, params)
        
        return True, f"You are now following {username_to_follow}!"
        
    def unfollow_user(self, username_to_unfollow):
        """UC-6: Unfollow a user"""
        if self.current_user is None:
            return False, "You must be logged in to unfollow users!"
            
        # Check if actually following
        query = """
        MATCH (a:User {screen_name: $current_user})-[r:FOLLOWS]->(b:User {screen_name: $username})
        RETURN r
        """
        
        params = {
            "current_user": self.current_user['screen_name'],
            "username": username_to_unfollow
        }
        
        result = self.db.execute_query(query, params)
        
        if not result:
            return False, "You are not following this user!"
            
        # Delete follow relationship
        query = """
        MATCH (a:User {screen_name: $current_user})-[r:FOLLOWS]->(b:User {screen_name: $username})
        DELETE r
        
        // Update follower/following counts
        SET a.friends_count = CASE WHEN a.friends_count > 0 THEN a.friends_count - 1 ELSE 0 END,
            b.followers_count = CASE WHEN b.followers_count > 0 THEN b.followers_count - 1 ELSE 0 END
            
        RETURN a, b
        """
        
        result = self.db.execute_query(query, params)
        
        return True, f"You have unfollowed {username_to_unfollow}!"
        
    def view_connections(self):
        """UC-7: View followers and following"""
        if self.current_user is None:
            return False, "You must be logged in to view connections!"
            
        username = self.current_user['screen_name']
        
        query_followers = """
        MATCH (a:User)-[r:FOLLOWS]->(b:User {screen_name: $username})
        RETURN a.screen_name AS follower
        """
        
        query_following = """
        MATCH (a:User {screen_name: $username})-[r:FOLLOWS]->(b:User)
        RETURN b.screen_name AS following
        """
        
        followers = self.db.execute_query(query_followers, {"username": username})
        following = self.db.execute_query(query_following, {"username": username})
        
        followers_list = [record['follower'] for record in followers]
        following_list = [record['following'] for record in following]
        
        return True, {"followers": followers_list, "following": following_list}
        
    def get_mutual_connections(self, other_username):
        """UC-8: View mutual connections"""
        if self.current_user is None:
            return False, "You must be logged in to view mutual connections!"
            
        username = self.current_user['screen_name']
        
        # Get mutual followers
        query = """
        MATCH (a:User {screen_name: $username})-[:FOLLOWS]->(c:User)<-[:FOLLOWS]-(b:User {screen_name: $other_username})
        RETURN c.screen_name AS mutual
        """
        
        params = {
            "username": username,
            "other_username": other_username
        }
        
        result = self.db.execute_query(query, params)
        
        mutuals = [record['mutual'] for record in result]
        
        return True, mutuals
        
    def get_friend_recommendations(self):
        """UC-9: Friend recommendations based on common connections"""
        if self.current_user is None:
            return False, "You must be logged in to get recommendations!"
            
        username = self.current_user['screen_name']
        
        # Get friend recommendations based on common connections
        query = """
        MATCH (me:User {screen_name: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(recommended:User)
        WHERE NOT (me)-[:FOLLOWS]->(recommended) AND me <> recommended
        RETURN recommended.screen_name AS recommendation, count(*) AS common_connections
        ORDER BY common_connections DESC
        LIMIT 5
        """
        
        result = self.db.execute_query(query, {"username": username})
        
        recommendations = [(record['recommendation'], record['common_connections']) for record in result]
        
        return True, recommendations
        
    def search_users(self, search_term):
        """UC-10: Search for users by name or username"""
        query = """
        MATCH (u:User)
        WHERE u.name CONTAINS $search_term OR u.screen_name CONTAINS $search_term
        RETURN u.screen_name AS username, u.name AS name, u.followers_count AS followers
        ORDER BY u.followers_count DESC
        LIMIT 10
        """
        
        result = self.db.execute_query(query, {"search_term": search_term})
        
        users = [(record['username'], record['name'], record['followers']) for record in result]
        
        return True, users
        
    def get_popular_users(self):
        """UC-11: Find popular users (most followed)"""
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (:User)-[:FOLLOWS]->(u)
        WITH u, count(*) AS followers
        RETURN u.screen_name AS username, u.name AS name, followers
        ORDER BY followers DESC
        LIMIT 10
        """
        
        result = self.db.execute_query(query)
        
        users = [(record['username'], record['name'], record['followers']) for record in result]
        
        return True, users 