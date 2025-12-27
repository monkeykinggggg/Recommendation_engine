from dataclasses import dataclass
from typing import Optional

@dataclass
class Neo4jConfig: 
    uri: str = "neo4j://127.0.0.1:7687"
    user: str = "neo4j"
    password: str = "Passw0rd"

@dataclass
class EmbeddingConfig: 
    fastrp_dimensions: int = 128
    fastrp_iteration_weights: list = None
    sbert_model:  str = "all-MiniLM-L6-v2"
    
    def __post_init__(self):
        if self.fastrp_iteration_weights is None: 
            self.fastrp_iteration_weights = [0.0, 1.0, 1.0]

@dataclass
class RecommenderConfig: 
    top_k: int = 10
    min_common_items: int = 2  # For collaborative filtering
    similarity_threshold: float = 0.5