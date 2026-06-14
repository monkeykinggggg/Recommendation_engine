from engine.config.settings import Neo4jConfig, RecommenderConfig
from engine.database.connection import Neo4jConnection
from engine.recommenders.enhanced_model_based import EnhancedModelBasedRecommender
from engine.embeddings.graph_embeddings import GraphEmbeddingGenerator
from engine.embeddings.semantic_embeddings import SemanticEmbeddingGenerator
from engine.config.settings import EmbeddingConfig

def main():
    # Initialize configuration
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    
    # storing review embeddings inside neo4j
    # semandic_generator = SemanticEmbeddingGenerator(db)
    # semandic_generator.generate_review_embeddings()
    # semandic_generator.set_zero_embeddings_for_users_and_products()
    
    try:
        # Initialize recommenders
        print("Initializing recommenders...")
        
        semantic_model_based = EnhancedModelBasedRecommender(db, for_production=False)
        semantic_model_based.setup_projection()
        
        metrics = semantic_model_based.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
        print(metrics)
        
        metrics = semantic_model_based.evaluate_performance(semantic_model_based.get_all_users_ids())
        print(metrics)
        

        
    finally:
        db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__": 
    main()