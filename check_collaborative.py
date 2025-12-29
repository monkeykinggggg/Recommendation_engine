from config.settings import Neo4jConfig
from database.connection import Neo4jConnection
from recommenders.collaborative import CollaborativeFilteringRecommender

def main():
    # Initialize configuration
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    
    try:
        # Initialize recommenders
        print("Initializing recommenders...")
        
        collaborative = CollaborativeFilteringRecommender(db)
        result = collaborative.recommend_training(user_id="AH3BXW7KLIS2VAE56UXJS2NS7I5A")
        for row in result:
            print(row)
            
        print("\nSwitching to production recommendations...\n")
        result = collaborative.recommend_production(user_id="AH3BXW7KLIS2VAE56UXJS2NS7I5A")
        for row in result:
            print(row)
        print("Evaluation completed.")
        
        metrics = collaborative.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
        print(metrics)
        
        metrics = collaborative.evaluate_performance(collaborative.get_all_users_ids())
        print(metrics)
        
        
    finally:
        db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__": 
    main()