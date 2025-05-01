import os
import sys
from getpass import getpass
from prettytable import PrettyTable
from db import Neo4jConnection
from user import UserManager

class SocialNetworkApp:
    def __init__(self):
        self.db = Neo4jConnection()
        self.user_manager = None
        
    def start(self):
        """Initialize the application"""
        print("\n===== Welcome to Social Network =====")
        
        if not self.db.connect():
            print("Failed to connect to the database. Please check your .env file.")
            sys.exit(1)
            
        self.user_manager = UserManager(self.db)
        
        self.main_menu()
        
    def main_menu(self):
        """Display the main menu"""
        while True:
            print("\n===== Main Menu =====")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":
                self.register_user()
            elif choice == "2":
                self.login_user()
            elif choice == "3":
                print("Thank you for using Social Network. Goodbye!")
                self.db.close()
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
                
    def register_user(self):
        """Register a new user"""
        print("\n===== User Registration =====")
        name = input("Enter your full name: ")
        email = input("Enter your email: ")
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        
        success, message = self.user_manager.register_user(name, email, username, password)
        
        if success:
            print(f"Success: {message}")
            print("Please login with your new account.")
        else:
            print(f"Error: {message}")
            
    def login_user(self):
        """Login an existing user"""
        print("\n===== User Login =====")
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        
        success, message = self.user_manager.login_user(username, password)
        
        if success:
            print(f"Success: {message}")
            self.user_menu()
        else:
            print(f"Error: {message}")
            
    def user_menu(self):
        """Display the user menu after login"""
        while True:
            print("\n===== User Menu =====")
            print("1. View Profile")
            print("2. Edit Profile")
            print("3. Follow a User")
            print("4. Unfollow a User")
            print("5. View Connections")
            print("6. View Mutual Connections")
            print("7. Get Friend Recommendations")
            print("8. Search Users")
            print("9. Explore Popular Users")
            print("10. Logout")
            
            choice = input("\nEnter your choice (1-10): ")
            
            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.edit_profile()
            elif choice == "3":
                self.follow_user()
            elif choice == "4":
                self.unfollow_user()
            elif choice == "5":
                self.view_connections()
            elif choice == "6":
                self.view_mutual_connections()
            elif choice == "7":
                self.get_friend_recommendations()
            elif choice == "8":
                self.search_users()
            elif choice == "9":
                self.explore_popular_users()
            elif choice == "10":
                self.user_manager.current_user = None
                print("Logged out successfully.")
                break
            else:
                print("Invalid choice. Please try again.")
                
    def view_profile(self):
        """View user profile"""
        print("\n===== View Profile =====")
        
        username = input("Enter username (leave blank for your profile): ")
        
        if username.strip() == "":
            success, profile = self.user_manager.view_profile()
        else:
            success, profile = self.user_manager.view_profile(username)
            
        if success:
            print("\nProfile Information:")
            table = PrettyTable()
            table.field_names = ["Field", "Value"]
            
            for key, value in profile.items():
                if key != "password":  # Don't show password
                    table.add_row([key, value])
                    
            print(table)
        else:
            print(f"Error: {profile}")
            
    def edit_profile(self):
        """Edit user profile"""
        print("\n===== Edit Profile =====")
        
        name = input("Enter new name (leave blank to keep current): ")
        bio = input("Enter new bio (leave blank to keep current): ")
        
        if not name and not bio:
            print("No changes to make.")
            return
            
        name = name if name else None
        bio = bio if bio else None
        
        success, message = self.user_manager.edit_profile(name, bio)
        
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")
            
    def follow_user(self):
        """Follow another user"""
        print("\n===== Follow User =====")
        
        username = input("Enter username to follow: ")
        
        success, message = self.user_manager.follow_user(username)
        
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")
            
    def unfollow_user(self):
        """Unfollow a user"""
        print("\n===== Unfollow User =====")
        
        username = input("Enter username to unfollow: ")
        
        success, message = self.user_manager.unfollow_user(username)
        
        if success:
            print(f"Success: {message}")
        else:
            print(f"Error: {message}")
            
    def view_connections(self):
        """View followers and following"""
        print("\n===== View Connections =====")
        
        success, connections = self.user_manager.view_connections()
        
        if success:
            followers = connections["followers"]
            following = connections["following"]
            
            print(f"\nFollowers ({len(followers)}):")
            if followers:
                for follower in followers:
                    print(f"- {follower}")
            else:
                print("No followers yet.")
                
            print(f"\nFollowing ({len(following)}):")
            if following:
                for followed in following:
                    print(f"- {followed}")
            else:
                print("Not following anyone yet.")
        else:
            print(f"Error: {connections}")
            
    def view_mutual_connections(self):
        """View mutual connections with another user"""
        print("\n===== Mutual Connections =====")
        
        username = input("Enter username to find mutual connections with: ")
        
        success, mutuals = self.user_manager.get_mutual_connections(username)
        
        if success:
            print(f"\nMutual Connections with {username} ({len(mutuals)}):")
            if mutuals:
                for mutual in mutuals:
                    print(f"- {mutual}")
            else:
                print("No mutual connections found.")
        else:
            print(f"Error: {mutuals}")
            
    def get_friend_recommendations(self):
        """Get friend recommendations"""
        print("\n===== Friend Recommendations =====")
        
        success, recommendations = self.user_manager.get_friend_recommendations()
        
        if success:
            print("\nPeople you might want to follow:")
            if recommendations:
                table = PrettyTable()
                table.field_names = ["Username", "Common Connections"]
                
                for username, common in recommendations:
                    table.add_row([username, common])
                    
                print(table)
            else:
                print("No recommendations at this time.")
        else:
            print(f"Error: {recommendations}")
            
    def search_users(self):
        """Search for users"""
        print("\n===== Search Users =====")
        
        search_term = input("Enter search term: ")
        
        success, users = self.user_manager.search_users(search_term)
        
        if success:
            print(f"\nSearch Results for '{search_term}':")
            if users:
                table = PrettyTable()
                table.field_names = ["Username", "Name", "Followers"]
                
                for username, name, followers in users:
                    table.add_row([username, name, followers])
                    
                print(table)
            else:
                print("No users found matching your search term.")
        else:
            print(f"Error: {users}")
            
    def explore_popular_users(self):
        """Find popular users"""
        print("\n===== Popular Users =====")
        
        success, users = self.user_manager.get_popular_users()
        
        if success:
            print("\nMost Popular Users:")
            if users:
                table = PrettyTable()
                table.field_names = ["Username", "Name", "Followers"]
                
                for username, name, followers in users:
                    table.add_row([username, name, followers])
                    
                print(table)
            else:
                print("No users found.")
        else:
            print(f"Error: {users}")

if __name__ == "__main__":
    app = SocialNetworkApp()
    app.start() 