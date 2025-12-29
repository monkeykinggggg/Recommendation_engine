from config.settings import Neo4jConfig, RecommenderConfig
from database.connection import Neo4jConnection
from recommenders. content_based import ContentBasedRecommender
from embeddings.semantic_embeddings import SemanticEmbeddingGenerator

def main():
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    
    se = SemanticEmbeddingGenerator(db)
    cb = ContentBasedRecommender(db)
    # checking semantic embedding class
    # se.generate_product_embeddings()
    # se.create_vector_index()
    
    # checking sample recommendations
    # result = cb.recommend_similar_products(product_id="B0941YDPSW")
    # print(result)
    # result2 = cb.recommend_by_query("face cream")
    # print(result2)
    
    # evaluation of the model
    metrics = cb.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
    print(metrics)
    
    metrics = cb.evaluate_performance(cb.get_all_users_ids())
    print(metrics)
    

if __name__ == "__main__":
    main()