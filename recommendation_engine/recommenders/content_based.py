from typing import List, Dict, Any, Optional
from engine.recommenders.base import BaseRecommender
from engine.embeddings.semantic_embeddings import SemanticEmbeddingGenerator
from engine.config.settings import RecommenderConfig


class ContentBasedRecommender(BaseRecommender):
    """
    Content-based recommender using semantic text embeddings.
    Uses Neo4j vector index for fast similarity search.
    
    Delegates embedding operations to TextEmbeddingGenerator.
    """
    
    def __init__(self, db, config=None):
        super().__init__(db)
        self.config = config or RecommenderConfig()
        # to be done: add semantic embedding generator with its configuration
        self.embedding_generator = SemanticEmbeddingGenerator(db)
    
    def get_name(self) -> str:
        return "Content-Based (Semantic Embeddings)"
    
    def recommend_similar_products(self, product_id: str, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recommend products semantically similar to the given product.
        Uses Neo4j vector index for fast search.
        
        Args:
            product_id: The product currently being viewed (parent_asin)
            user_id: Optional - exclude products already rated by this user
        """
        # zwracamy embedding ogladanego produktu
        source = self.db.execute_query(f"""
            MATCH (p:Product {{parent_asin:  $product_id}})
            RETURN p.{self.embedding_generator.config.embedding_property_name} AS embedding
        """, {"product_id": product_id})
        
        if not source or not source[0].get("embedding"):
            print(f"Product {product_id} has no embedding.  Setup embeddings and indexes first.")
            return []
        embedding = source[0]["embedding"]
            
        query = f"""
            CALL db.index.vector.queryNodes($index_name, $k, $embedding)
            YIELD node, score
            WHERE node.parent_asin <> $product_id
            {self.get_user_filter() if user_id else ""}
            RETURN node.parent_asin AS parent_asin,
            node.title AS title,
            node.images[0] as image_representative,
            score AS semantic_similarity
            ORDER BY semantic_similarity DESC
            LIMIT $limit
        """
        params = {
            "index_name": self.embedding_generator.config.vector_index_name,
            "embedding": embedding,
            "product_id": product_id,
            "k": limit + 10,
            "limit": limit
        }
        if user_id: 
            params["user_id"] = user_id
        
        return self.db.execute_query(query, params)
    
    def get_user_filter(self):
        filter = """
            AND NOT EXISTS {
                MATCH (u:User {user_id: $user_id})-[:RATED]->(node)
            }
        """
        return filter

    def recommend_by_query(self, query_text: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recommend products based on a text query.
        Embeds the query and finds semantically similar products. 
        
        Args: 
            query_text: User's search query (e.g., "moisturizing face cream")
            user_id: Optional - exclude products already rated by this user
        """
        print(f"Searching for:  '{query_text}'")
        query_embedding = self.embedding_generator.embed_text(query_text)
        
        query = f"""
            CALL db.index.vector.queryNodes($index_name, $k, $embedding)
            YIELD node, score
            WHERE true {self.get_user_filter() if user_id else ""}
            RETURN node.parent_asin AS parent_asin, 
            node.title AS title,
            node.images[0] as image_representative,
            score AS semantic_similarity
            ORDER BY semantic_similarity DESC
            LIMIT $limit
        """
        
        params = {
            "index_name": self.embedding_generator.config.vector_index_name,
            "embedding": query_embedding,
            "k": 10 + 10,
            "limit": 10
        }
        if user_id:
            params["user_id"] = user_id
        
        return self.db.execute_query(query, params)
    
    def recommend_production(self, user_id: str,product_id: str) -> List[Dict[str, Any]]:
        """
        Production recommendation based on currently viewed product.
        Excludes products user has already rated. 
        """
        return self.recommend_similar_products(product_id, user_id)
    
    def recommend_training(self, user_id: str) -> List[Dict[str, Any]]: 
        """
        For evaluation:  recommend based on user's most recent training interaction.
        Excludes all products in user's training set.
        """
        
        # bierzemy ostatni produkt najwyzej oceniony z czesci zbioru train
        query = """
        MATCH (u:User {user_id: $user_id})-[r:RATED {split: 'train'}]->(p:Product)
        RETURN p.parent_asin AS parent_asin
        ORDER BY r.rating DESC, r.timestamp DESC
        LIMIT 1
        """
        query_result = self.db.execute_query(query, {"user_id": user_id})
        user_last_product_id = query_result[0]["parent_asin"]
        
        # Get recommendations excluding training products
        query = f"""
            MATCH (source:Product {{parent_asin: $product_id}})
            CALL db.index.vector.queryNodes($index_name, $k, source.{self.embedding_generator.config.embedding_property_name})
            YIELD node, score
            WHERE node <> source
            AND NOT EXISTS {{
                MATCH (u:User {{user_id: $user_id}})-[:RATED {{split: 'train'}}]->(node)
            }}
            RETURN node.parent_asin AS parent_asin, score AS similarity_score
            ORDER BY score DESC
            LIMIT $limit
        """
        
        return self.db.execute_query(query, {
            "product_id": user_last_product_id,
            "user_id": user_id,
            "index_name": self.embedding_generator.config.vector_index_name,
            "k": 20,
            "limit": 10
        })
    
    
    def evaluate_performance(self, test_users: List[str]) -> Dict[str, float]:
        """
        Evaluate using Leave-One-Out method.
        For each user, uses their last higly rated training product to predict test product.
        """
        hits = 0
        reciprocal_rank_sum = 0
        users_evaluated = 0

        print(f"Starting evaluation of Content-Based for {len(test_users)} users...")

        for i, user_id in enumerate(test_users):
            # Get test item
            test_query = """
                MATCH (u:User {user_id: $user_id})-[r:RATED {split: 'test'}]->(p: Product)
                RETURN p.parent_asin AS parent_asin
            """
            test_item = self.db.execute_query(test_query, {"user_id":  user_id})
            test_item_id = test_item[0]["parent_asin"]
            recommendations = self.recommend_training(user_id)
            rec_ids = [r["parent_asin"] for r in recommendations]

            if test_item_id in rec_ids:
                hits += 1
                rank = rec_ids.index(test_item_id) + 1
                reciprocal_rank_sum += 1 / rank
            
            users_evaluated += 1
            
            if (i + 1) % 200 == 0:
                print(f"  Evaluated {i + 1}/{len(test_users)}...")

        metrics = {
            "algorithm": self.get_name(),
            "hits": hits,
            "HR": hits / users_evaluated if users_evaluated > 0 else 0,
            "MRR": reciprocal_rank_sum / users_evaluated if users_evaluated > 0 else 0,
            "evaluated_count": users_evaluated
        }
        return metrics