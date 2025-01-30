# journal/utils.py  (Create this directory and file)
from neo4j import GraphDatabase
from django.conf import settings
from contextlib import contextmanager

class Neo4jDriver:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return result.data()

    @contextmanager
    def get_session(self):
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

neo4j_driver = Neo4jDriver()