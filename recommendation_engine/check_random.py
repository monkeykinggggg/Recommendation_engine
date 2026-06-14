from engine.config.settings import Neo4jConfig
from engine.database.connection import Neo4jConnection
from engine.recommenders.random_rec import RandomRecommender

def main():
    db_config = Neo4jConfig()
    db = Neo4jConnection(db_config)
    
    try:
        print("Initializing Random Baseline Recommender...")
        
        random_rec = RandomRecommender(db)
        
        # Test for single user
        print("\n--- Random recommendations for single user ---")
        result = random_rec.recommend_training(user_id="AH3BXW7KLIS2VAE56UXJS2NS7I5A")
        for row in result:
            print(row)
        
        print("\n--- Evaluation for single user ---")
        metrics = random_rec.evaluate_performance(["AH3BXW7KLIS2VAE56UXJS2NS7I5A"])
        print(metrics)
        
        print("\n--- Evaluation for all users ---")
        metrics = random_rec.evaluate_performance(random_rec.get_all_users_ids())
        print(metrics)
        
        print("\n Mean of evaluation for all users ")
        HR_list = []
        MRR_list = []
        for _ in range(10):
            metrics = random_rec.evaluate_performance(random_rec.get_all_users_ids())
            HR_list.append(metrics["HR"])
            MRR_list.append(metrics["MRR"])
        print(f"Average HR over 10 runs: {sum(HR_list)/len(HR_list)}")
        print(f"Average MRR over 10 runs: {sum(MRR_list)/len(MRR_list)}")
        
    finally:
        db.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
