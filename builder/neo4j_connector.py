"""
Neo4j database handler for storing and querying the knowledge graph.
"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class Neo4jConnector:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'),
            auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
        )
    def close(self):
        self.driver.close()
    def create_node(self, label, properties):
        with self.driver.session() as session:
            session.run(f"CREATE (n:{label} $props)", props=properties)
    # Add more methods as needed

if __name__ == "__main__":
    db = Neo4jConnector()
    db.create_node('Test', {'name': 'Example'})
    db.close()
