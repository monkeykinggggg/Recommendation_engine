from typing import List, Dict, Any
from recommenders.base import BaseRecommender   # Zakładam, że masz klasę bazową

class CollaborativeFilteringRecommender(BaseRecommender):
    """
    Zoptymalizowana implementacja User-Based CF w czystym Cypher.
    Obsługuje tryb ewaluacji (tylko train) oraz tryb produkcyjny (wszystkie dane).
    """

    def get_name(self) -> str:
        return "Collaborative Filtering (User-Based)"
    
    def get_query(self, train_only: bool) -> str:
        relatinship_filter = "{split:'train'}" if train_only else ""
        query = f"""
        // tworzymy mape ocen wybranego uzytkownika
        MATCH (target:User {"{user_id: $user_id}"})-[r1:RATED{relatinship_filter}]->(p:Product)
        WITH target, collect({'{product:  p.parent_asin, rating: r1.rating}'}) AS targetRatingsMap

        // szukamy uzytkownikow ktorzy ocenili wspolne produkty
        MATCH (target)-[:RATED{relatinship_filter}]->(common:Product)<-[r2:RATED{relatinship_filter}]-(other:User)
        WHERE other <> target
        WITH target, targetRatingsMap, other, count(common) AS commonProducts,
        collect({'{product:common.parent_asin, targetRating:[(target)-[r:RATED]->(common)|r.rating][0], otherRating:r2.rating}'}) AS commonRatingsMap
        WHERE commonProducts >= $minProducts  // mozemy ustawic ile powinni uzytkownicy miec przynajmniej wspolnych produktow

        // return target.user_id, targetRatingsMap,commonProducts, commonRatingsMap, other.user_id;

        // teraz liczymy podobienstwo na podstawie mapy wspolnych ocen
        WITH target, other, commonProducts, commonRatingsMap,
        reduce(s = 0.0, x IN commonRatingsMap | s + x.targetRating * x.otherRating) AS dotProduct,
        sqrt(reduce(s = 0.0, x IN commonRatingsMap | s + x.targetRating * x. targetRating)) AS targetNorm,
        sqrt(reduce(s = 0.0, x IN commonRatingsMap | s + x.otherRating * x.otherRating)) AS otherNorm
                
        WITH target, other, commonRatingsMap,
        CASE WHEN targetNorm * otherNorm = 0 THEN 0
            ELSE dotProduct / (targetNorm * otherNorm) 
        END AS similarity
        // return target, similarity, other, commonRatingsMap;

        MATCH (other)-[r:RATED{relatinship_filter}]->(rec:Product)
        WHERE NOT (target)-[:RATED{relatinship_filter}]->(rec)
        WITH rec,
        sum(similarity*r.rating) AS weightedScore,
        sum(similarity) AS totalWeight,
        count(DISTINCT other) AS recommenderCount

        return rec.parent_asin AS parent_asin,
        weightedScore/totalWeight AS predicted_score,
        recommenderCount AS similar_users_count
        ORDER BY predicted_score DESCENDING
        LIMIT 10;
        """
        return query

    def recommend_training(self, user_id: str, minProducts: int = 3) -> List[Dict[str, Any]]:
        query = self.get_query(train_only=True)
        return self.db.execute_query(query, {"user_id": user_id, "minProducts": minProducts})

    def recommend_production(self, user_id: str, minProducts: int = 3) -> List[Dict[str, Any]]:
        query = self.get_query(train_only=False)
        return self.db.execute_query(query, {"user_id": user_id, "minProducts": minProducts})
    
    
    def evaluate_performance(self, test_users: List[str], top_k: int = 10) -> Dict[str, float]:
        """
        Ocenia algorytm metodą Leave-One-Out.
        Dla każdego usera sprawdzamy, czy jego jedyny produkt 'test' 
        pojawia się w rekomendacjach wygenerowanych na podstawie 'train'.
        """
        hits = 0
        reciprocal_rank_sum = 0
        users_evaluated = 0

        print(f"Rozpoczynam ewaluację CF dla {len(test_users)} użytkowników...")

        for user_id in test_users:
            # A. Pobierz ten jeden 'ukryty' produkt ze zbioru TEST
            test_item_query = """
            MATCH (u:User {user_id: $user_id})-[r:RATED{split:'test'}]->(p:Product) 
            RETURN p.parent_asin AS parent_asin
            """
            test_item = self.db.execute_query(test_item_query, {"user_id": user_id})
                
            test_item_id = test_item[0]["parent_asin"]
            recommendations = self.recommend_training(user_id=user_id)
            rec_ids = [r["parent_asin"] for r in recommendations]

            # C. Sprawdź czy trafiliśmy
            if test_item_id in rec_ids:
                hits += 1
                rank = rec_ids.index(test_item_id) + 1
                reciprocal_rank_sum += 1/rank
            
            users_evaluated += 1

        # Obliczanie średnich
        metrics = {
            "algorithm": self.get_name(),
            "hits": hits,
            "HR": hits / users_evaluated,                 # Hit Rate @ K
            "MRR": reciprocal_rank_sum / users_evaluated, # Mean Reciprocal Rank
            "evaluated_count": users_evaluated
        }
        
        return metrics
    
    def get_all_users_ids(self) -> List[str]:
        query = """
        MATCH (u:User)
        RETURN u.user_id AS user_id
        """
        results = self.db.execute_query(query)
        return [r["user_id"] for r in results]

