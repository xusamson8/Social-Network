# Social Network Application

CS157C Semester-Long Project Using Neo4j

A Python console-based social network application that uses Neo4j as a graph database to model relationships between users.

## Features

This application implements the following use cases:

### User Management
- UC-1: User Registration - Sign up with basic details
- UC-2: User Login - Authenticate and access account
- UC-3: View Profile - View user profile information
- UC-4: Edit Profile - Update profile details

### Social Graph Features
- UC-5: Follow Another User - Create FOLLOWS relationship
- UC-6: Unfollow a User - Remove FOLLOWS relationship
- UC-7: View Friends/Connections - See followers and following
- UC-8: Mutual Connections - View mutual friends
- UC-9: Friend Recommendations - Get suggestions based on common connections

### Search & Exploration
- UC-10: Search Users - Find users by name or username
- UC-11: Explore Popular Users - See most-followed users

## Prerequisites

- Python 3.7+
- JDK 11 
- Neo4j Database (4.0+)
- Twitter dataset loaded into Neo4j (from [neo4j-graph-examples/twitter-v2](https://github.com/neo4j-graph-examples/twitter-v2/blob/main/data/twitter-v2-43.dump))

## Installation

1. Clone the repository:
```
git clone ...

```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. On Neo4j Desktop...
- Create a local DBMS 
 - name it twitter, and set the password to SocialNetwork
 - Select version 4.4.19? 
 - create the local dbms

- click the DBMS, install the APOC plugin (on plugins tab) to synthesize follower data (in future steps)

Configure the database connection:
   - Edit the `.env` file with the following credentials based on build:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=SocialNetwork
   NEO4J_DATABASE=neo4j 
   ```

   - install the dump file on the repo, open the terminal in neo4j and paste this command
    - bin/neo4j-admin load --from=/path/to/dump --database=neo4j --force

## Usage

1. Run the DBMS and Start the application:
```
python app.py
```

2. Follow the on-screen prompts to:
   - Register a new user or login
   - Navigate through various features
   - Interact with other users

## Loading Data

This application is designed to work with the Twitter dataset provided by Neo4j Graph Examples.

To load the dataset:

1. Download the dataset from [neo4j-graph-examples/twitter-v2](https://github.com/neo4j-graph-examples/twitter-v2)
2. Follow the instructions in the repository to import the data into your Neo4j instance

### (Recommended) Synthesize Follower Data 
- to reduce the skew and have more followers for other users...
- open neo4j browser for this DBMS, paste the following command as a chunk 
```
// Step 1: Match active users with low follower count
MATCH (u:User)
WHERE u.screen_name <> 'neo4j'
WITH collect(u) AS users
UNWIND users AS follower
WITH follower, users
// Step 2: Pick 5 random users to follow (not self, not already following)
UNWIND apoc.coll.randomItems(users, 5, false) AS followee
WITH follower, followee
WHERE follower <> followee AND NOT (follower)-[:FOLLOWS]->(followee)
// Step 3: Create the FOLLOWS relationship
MERGE (follower)-[:FOLLOWS]->(followee)
```

## Project Structure

- `app.py` - Main application entry point and console interface
- `db.py` - Neo4j database connection module
- `user.py` - User management functionality
- `requirements.txt` - Python dependencies
- `.env` - Environment variables for configuration 