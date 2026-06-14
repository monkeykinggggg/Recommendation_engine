from typing import List, Dict, Any
from engine.recommenders.base import BaseRecommender


class RandomRecommender(BaseRecommender):
    """
    Random baseline recommender that returns 10 random products.
    This is the absolute minimum baseline - any real algorithm should beat this.
    """

    def get_name(self) -> str:
        return "Random (Baseline)"

    def recommend_training(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Recommend 10 random products from training data,
        excluding products the user has already rated in training.
        """
        query = """
        MATCH (me:User {user_id: $userId})
        MATCH (p:Product)<-[r:RATED {split: 'train'}]-(:User)
        WHERE NOT EXISTS { (me)-[:RATED {split: 'train'}]->(p) }
        WITH DISTINCT p
        RETURN p.parent_asin AS parent_asin, rand() AS predicted_score
        ORDER BY predicted_score DESC
        LIMIT 10
        """
        return self.db.execute_query(query, {"userId": user_id})

    def recommend_production(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Recommend 10 random products from all data,
        excluding products the user has already rated.
        """
        query = """
        MATCH (me:User {user_id: $userId})
        MATCH (p:Product)<-[r:RATED]-(:User)
        WHERE NOT EXISTS { (me)-[:RATED]->(p) }
        WITH DISTINCT p
        RETURN p.parent_asin AS parent_asin, rand() AS predicted_score
        ORDER BY predicted_score DESC
        LIMIT 10
        """
        return self.db.execute_query(query, {"userId": user_id})

    def evaluate_performance(self, test_users: List[str]) -> Dict[str, float]:
        """
        Evaluate the algorithm using Leave-One-Out method.
        For each user, check if their single 'test' product 
        appears in the recommendations generated from 'train'.
        """
        hits = 0
        reciprocal_rank_sum = 0
        users_evaluated = 0

        print(f"Starting evaluation of Random Baseline for {len(test_users)} users...")

        for user_id in test_users:
            # Get the 'hidden' product from TEST set
            test_item_query = """
            MATCH (u:User {user_id: $user_id})-[r:RATED{split:'test'}]->(p:Product) 
            RETURN p.parent_asin AS parent_asin
            """
            test_item = self.db.execute_query(test_item_query, {"user_id": user_id})
            test_item_id = test_item[0]["parent_asin"]
            
            recommendations = self.recommend_training(user_id)
            rec_ids = [r["parent_asin"] for r in recommendations]

            if test_item_id in rec_ids:
                hits += 1
                rank = rec_ids.index(test_item_id) + 1
                reciprocal_rank_sum += 1 / rank

            users_evaluated += 1

        metrics = {
            "algorithm": self.get_name(),
            "hits": hits,
            "HR": hits / users_evaluated,
            "MRR": reciprocal_rank_sum / users_evaluated,
            "evaluated_count": users_evaluated
        }
        return metrics
