import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self._driver = None
        
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print(f"Successfully connected to Neo4j database: {self.uri}")
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j database: {e}")
            return False
            
    def close(self):
        """Close the connection to Neo4j"""
        if self._driver is not None:
            self._driver.close()
            
    def execute_query(self, query, parameters=None):
        """Execute a Cypher query and return the results"""
        if self._driver is None:
            raise Exception("Driver not initialized. Call connect() first.")
            
        if parameters is None:
            parameters = {}
            
        with self._driver.session(database=self.database) as session:
            results = session.run(query, parameters)
            return [record for record in results] 