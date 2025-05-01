from db import Neo4jConnection

def init_database():
    """Initialize the database with constraints and indexes"""
    db = Neo4jConnection()
    
    if not db.connect():
        print("Failed to connect to the database.")
        return False
    
    print("Connected to database. Creating constraints and indexes...")
    
    constraints = [
        "CREATE CONSTRAINT user_screen_name_unique IF NOT EXISTS ON (u:User) ASSERT u.screen_name IS UNIQUE",
        "CREATE CONSTRAINT user_email_unique IF NOT EXISTS ON (u:User) ASSERT u.email IS UNIQUE"
    ]
    
    indexes = [
        "CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name)",
        "CREATE INDEX user_followers_idx IF NOT EXISTS FOR (u:User) ON (u.followers_count)"
    ]
    
    for query in constraints + indexes:
        try:
            db.execute_query(query)
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Error executing {query}: {e}")
    
    print("Database initialization completed.")
    db.close()
    return True

if __name__ == "__main__":
    init_database() 