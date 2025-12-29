from config.settings import Neo4jConfig
from database.connection import Neo4jConnection
from recommenders.popularity import PopularityRecommender

def main():
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    
    try:
        print("Initializing Popularity Baseline Recommender...")
        
        popularity = PopularityRecommender(db)
        
        # Test for single user
        print("\n--- Training recommendations for single user ---")
        result = popularity.recommend_training(user_id="AH3BXW7KLIS2VAE56UXJS2NS7I5A")
        for row in result:
            print(row)
        
        print("\n--- Evaluation for single user ---")
        metrics = popularity.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
        print(metrics)
        
        print("\n--- Evaluation for all users ---")
        metrics = popularity.evaluate_performance(popularity.get_all_users_ids())
        print(metrics)
        
    finally:
        db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
