from typing import List, Dict, Any
from recommenders.base import BaseRecommender
from embeddings.graph_embeddings import GraphEmbeddingGenerator
from config.settings import RecommenderConfig

class ModelBasedRecommender(BaseRecommender):
    """
    Model-based recommender using FastRP graph embeddings and KNN. 
    Uses cosine similarity between user and product embeddings. 
    """
    
    def __init__(self, db, config=None, production_graph: bool = True):
        super().__init__(db)
        self.embedding_generator = GraphEmbeddingGenerator(db, config, production_graph)
        self.config = config or RecommenderConfig()
    
    def get_name(self) -> str:
        return "Model-Based (FastRP + KNN)"

    
    def run_knn(self) -> List[Dict[str, Any]]: 
        """
        Use GDS KNN algorithm for finding similar nodes.
        """
        print("Setting up embeddings...")
        self.embedding_generator.setup_embeddings()
        
        print("Cleaning old SIMILAR relationships...")
        self.db.execute_query("MATCH ()-[r:SIMILAR]->() DELETE r")
        
        print("Running KNN to write similarity for users...")
        # First, run KNN to create similarity relationships
        # we compute similarity only between users (nodeLabels)
        knn_query = """
        CALL gds.knn.write(
            $graph_name, 
            {
            nodeLabels: ['User'],
            nodeProperties: {fastrp_embedding:'COSINE'},
            writeRelationshipType: 'SIMILAR',
            writeProperty: 'score',
            sampleRate: $sample_rate,
            topK: $top_k,
            randomSeed: 42,
            concurrency: 1
            }
        )
        YIELD nodesCompared, ranIterations, nodePairsConsidered, relationshipsWritten, similarityDistribution
        RETURN nodesCompared, ranIterations, nodePairsConsidered, relationshipsWritten, similarityDistribution
        """
        
        return self.db.execute_query(knn_query, {
            "graph_name": self.embedding_generator.graph_name,
            "top_k":  self.config.top_k,
            "sample_rate": 1.0, 
        })
    
    def find_similar_users(self):
        query = """
        MATCH (u1:User)-[r:SIMILAR]->(u2:User)
        RETURN u1.user_id AS person1, u2.user_id AS person2, r.score AS similarity
        ORDER BY similarity DESCENDING, person1, person2
        LIMIT 50
        """
        return self.db.execute_query(query)
    
    def recommend_production(self, user_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (me:User {user_id: $userId})-[s:SIMILAR]-(similar:User)
        MATCH (similar)-[r:RATED]->(product:Product)
        WHERE NOT EXISTS { (me)-[:RATED]->(product) }  // Exclude already rated
        //AND r.rating >= 4.0  // Only highly rated products
        WITH product, 
            SUM(s.score * r.rating) AS weighted_sum,
            SUM(s.score) AS similarity_sum,
            COUNT(similar) AS similar_users_count
        
        RETURN product.parent_asin AS parent_asin,
               weighted_sum / similarity_sum AS predicted_score,
               similar_users_count
        ORDER BY predicted_score DESC
        LIMIT 10
        """
        print("Generating product recommendations...")
        return self.db.execute_query(query, {
            "userId": user_id
        })
        
    def recommend_training(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate recommendations using only training data.
        Excludes products the user rated in training set.
        """
        query = """
        MATCH (me:User {user_id: $userId})-[s:SIMILAR]-(similar:User)
        MATCH (similar)-[r:RATED {split: 'train'}]->(product:Product)
        WHERE NOT EXISTS { (me)-[:RATED {split: 'train'}]->(product) }
        WITH product, 
            SUM(s.score * r.rating) AS weighted_sum,
            SUM(s.score) AS similarity_sum,
            COUNT(similar) AS similar_users_count
        
        RETURN product.parent_asin AS parent_asin,
               weighted_sum / similarity_sum AS predicted_score,
               similar_users_count
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

        print(f"Starting evaluation of Model-Based Recommender for {len(test_users)} users...")
        
        # Setup embeddings using only training data
        self.embedding_generator = GraphEmbeddingGenerator(self.db,  for_production=False)
        self.run_knn()

        for user_id in test_users:
            # A. Get that one 'hidden' product from TEST set
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
                reciprocal_rank_sum += 1/rank
            
            users_evaluated += 1

        # Calculate averages
        metrics = {
            "algorithm": self.get_name(),
            "hits": hits,
            "HR": hits / users_evaluated if users_evaluated > 0 else 0,                 
            "MRR": reciprocal_rank_sum / users_evaluated if users_evaluated > 0 else 0  , 
            "evaluated_count": users_evaluated
        }
        return metrics