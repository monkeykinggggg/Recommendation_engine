from abc import ABC, abstractmethod
from typing import List, Dict, Any
from database.connection import Neo4jConnection

class BaseRecommender(ABC):
    """Abstract base class for all recommenders"""
    
    def __init__(self, db:  Neo4jConnection):
        self.db = db
        self.gds = db.gds
        self.training_graph_name="train_graph"
    
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the recommender"""
        pass
    
    def get_all_users_ids(self) -> List[str]:
        query = """
        MATCH (u:User)
        RETURN u.user_id AS user_id
        """
        results = self.db.execute_query(query)
        return [r["user_id"] for r in results]
    
    def get_user_history(self, user_id: str) -> List[str]:
        """Get products the user has already rated"""
        query = """
        MATCH (u: User {user_id: $user_id})-[:RATED]->(p:Product)
        RETURN p.parent_asin AS product_id
        """
        results = self.db.execute_query(query, {"user_id": user_id})
        return [r["product_id"] for r in results]
    
    def drop_evaluation_graph(self):
        """Drops the Training Graph from GDS memory."""
        exists_result = self.gds.graph.exists(self.training_graph_name)
        if exists_result["exists"]:
            print(f"Dropping graph '{self.training_graph_name}' from GDS memory...")
            self.gds.graph.drop(self.gds.graph.get(self.training_graph_name))
        else:
            print(f"Graph '{self.training_graph_name}' does not exist in GDS memory. No action taken.")
    
    def create_evaluation_graph(self):
        """Projects the Training Graph into GDS memory."""
        exists_result = self.gds.graph.exists(self.training_graph_name)
        if not exists_result["exists"]:
            print(f"Projecting '{self.training_graph_name}'...")
            
            node_query = """
            MATCH (n) WHERE n:User OR n:Product RETURN id(n) AS id
            """
            
            rel_query = """
            MATCH (n)-[r:RATED]->(m)
            RETURN id(n) AS source, id(m) AS target, 
            r.rating as rating,
            CASE 
                WHEN r.split = "train" THEN "RATED_TRAIN"
                ELSE "RATED_TEST"
            END AS type
            """
            
            try:
                G, result = self.gds.graph.project.cypher(
                    self.training_graph_name,
                    node_query,
                    rel_query
                )
                print(f"Graph {G.name()} projected! Nodes: {G.node_count()}, Edges: {G.relationship_count()}")
                return G
            except Exception as e:
                print(f"Error projecting graph: {e}")
                raise e
            
        else:
            print(f"Graph '{self.training_graph_name}' already exists in GDS memory.")
            return self.gds.graph.get(self.training_graph_name)