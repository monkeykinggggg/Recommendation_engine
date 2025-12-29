from config.settings import Neo4jConfig, RecommenderConfig
from database.connection import Neo4jConnection
from recommenders.model_based import ModelBasedRecommender
from embeddings.graph_embeddings import GraphEmbeddingGenerator
from config.settings import EmbeddingConfig

def main():
    # Initialize configuration
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    embedding_generator = GraphEmbeddingGenerator(db)
    
    try:
        # Initialize recommenders
        print("Initializing recommenders...")
        
        model_based = ModelBasedRecommender(db, production_graph=False)
        metrics = model_based.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
        print(metrics)
        
        metrics = model_based.evaluate_performance(model_based.get_all_users_ids())
        print(metrics)
        

        
    finally:
        db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__": 
    main()