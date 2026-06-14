from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Neo4jConfig: 
    uri: str = "neo4j://127.0.0.1:7687"
    user: str = "neo4j"
    password: str = "Passw0rd"

@dataclass
class EmbeddingConfig: 
    # for fastRP algorithm
    embedding_dimensions: int = 32   #dlugosc wyprodukowanego wektora osadzen, im wiecej wymiarow tym wiecej informacji moze byc zakodowane w wektorze, ale zwieksza to tez wymagania pamieciowe i obliczeniowe liniowo
    iteration_weights: List[float] = field(default_factory=lambda: [0.0, 1.0, 1.0, 0.8])   # wagi dla kolejnych iteracji algorytmu FastRP, okreslaja jak bardzo nastepne embeddingi posrednie wplywaja na istateczny wektor; przez ten wektor rowniez okreslamy ile algorytm bedzie mial iteracji
    random_seed: int = 42  # musi być ustawiony również gdy dodajemy wpływ parametrów węzła na algorytm
    
    # for semantic product embeddings
    sbert_model_name:  str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384  # For 'all-MiniLM-L6-v2'
    batch_size: int = 64
    vector_index_name: str = "product_semantic_index"
    embedding_property_name: str = "semantic_embedding"
    
    # for review semantic embeddings embeddings
    review_embedding_property_name: str = "review_semantic_embedding"
    

@dataclass
class RecommenderConfig: 
    # model-based
    top_k: int = 2
    
    # For collaborative filtering
    min_common_items: int = 2  
    similarity_threshold: float = 0.5
    
    # for enhanced model-based
    embedding_dimensions: int = 1024   #dlugosc wyprodukowanego wektora osadzen, im wiecej wymiarow tym wiecej informacji moze byc zakodowane w wektorze, ale zwieksza to tez wymagania pamieciowe i obliczeniowe liniowo
    iteration_weights: List[float] = field(default_factory=lambda: [1.0, 0.5, 0.5, 0.0])   # wagi dla kolejnych iteracji algorytmu FastRP, okreslaja jak bardzo nastepne embeddingi posrednie wplywaja na istateczny wektor; przez ten wektor rowniez okreslamy ile algorytm bedzie mial iteracji
    random_seed: int = 42  # musi być ustawiony również gdy dodajemy wpływ parametrów węzła na algorytm
    property_ratio: float = 0.5  # ratio between the influence of node properties (how many embedddings) and all embeddings in FastRP
    self_influence: float = 0.5  # influence of the node itself in FastRP embeddings
    review_sample_rate: float = 0.8
    review_top_k: int = 2  