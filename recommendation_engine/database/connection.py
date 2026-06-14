from neo4j import GraphDatabase
from graphdatascience import GraphDataScience
from contextlib import contextmanager
from engine.config.settings import Neo4jConfig

class Neo4jConnection: 
    _instance = None
    
    def __new__(cls, config: Neo4jConfig = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance. config = config or Neo4jConfig()
            cls._instance.driver = GraphDatabase.driver(
                cls._instance.config.uri,
                auth=(cls._instance.config.user, cls._instance.config.password)
            )
            cls._instance.gds = GraphDataScience(
                cls._instance.config.uri,
                auth=(cls._instance.config.user, cls._instance.config.password)
            )
        return cls._instance
    
    @contextmanager
    def session(self):
        session = self.driver.session()
        try:
            yield session
        finally: 
            session.close()
    
    def close(self):
        self.driver.close()
        Neo4jConnection._instance = None
    
    def execute_query(self, query: str, parameters: dict = None):
        with self. session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]