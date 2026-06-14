from typing import List, Dict, Any
from engine.recommenders.base import BaseRecommender
from engine.embeddings.semantic_embeddings import SemanticEmbeddingGenerator
from engine.config.settings import RecommenderConfig


class EnhancedModelBasedRecommender(BaseRecommender):
    """
    Enhanced Model-based recommender using FastRP with semantic embeddings.
    
    Combines:
    - Graph structure (User-Review-Product relationships)
    - Review semantic embeddings (from Sentence Transformers)
    
    This allows FastRP to learn from both structure AND content.
    """
    
    def __init__(self, db, config:  RecommenderConfig = None, for_production: bool = True):
        super().__init__(db)
        self.config = config or RecommenderConfig()
        self.semantic_embedding_generator = SemanticEmbeddingGenerator(db)
        self.for_production = for_production
        self.graph_name = "enhanced_fastrp_prod" if for_production else "enhanced_fastrp_train"
    
    def get_name(self) -> str:
        return "Enhanced Model-Based (FastRP + Review Semantics)"
    
    def drop_graph_projection(self):
        """Drop in-memory graph projection if it exists."""
        query = """
        CALL gds.graph.exists($graph_name) YIELD exists
        RETURN exists
        """
        result = self.db.execute_query(query, {"graph_name": self.graph_name})
        
        if result and result[0].get("exists"):
            print(f"Dropping graph '{self.graph_name}' from GDS memory...")
            drop_query = """
            CALL gds.graph.drop($graph_name) YIELD graphName
            RETURN graphName
            """
            self.db.execute_query(drop_query, {"graph_name": self.graph_name})
            print(f"Graph '{self.graph_name}' dropped.")
        else:
            print(f"Graph '{self.graph_name}' does not exist.  No action taken.")
    
    
    def create_graph_projection_training(self):
        """
        Create graph projection for training (excludes test data).
        Includes Review nodes with semantic embeddings.
        Rating is used as edge weight to influence FastRP propagation.
        """
        
        # Node query: Users, Products, and Reviews (with embeddings)
        node_query = f"""
            MATCH (n) WHERE n:User OR n:Product OR n:Review
            RETURN id(n) AS id, labels(n) AS labels,
                    n.{self.semantic_embedding_generator.config.review_embedding_property_name} AS {self.semantic_embedding_generator.config.review_embedding_property_name}
        """
        
        # Relationship query: only training data, with rating as weight
        # Rating is used on both edges so higher-rated reviews have more influence
        rel_query = """
            MATCH (u:User)-[:WROTE]->(r:Review)-[:ABOUT]->(p:Product)
            WHERE r.split = 'train'
            RETURN id(u) AS source, id(r) AS target, r.rating AS weight, 'WROTE' AS type
            
            UNION ALL
            
            MATCH (u:User)-[:WROTE]->(r:Review)-[:ABOUT]->(p:Product)
            WHERE r.split = 'train'
            RETURN id(r) AS source, id(p) AS target, r.rating AS weight, 'ABOUT' AS type
        """
        
        print("Creating enhanced graph projection (training)...")
        create_query ="""
        CALL gds.graph.project.cypher(
            $graph_name,
            $node_query,
            $rel_query
        )
            YIELD graphName, nodeCount, relationshipCount
            RETURN graphName, nodeCount, relationshipCount
        """
        result = self.db.execute_query(create_query, {
            "graph_name": self.graph_name,
            "node_query": node_query,
            "rel_query": rel_query,
            "semantic_embedding_name": self.semantic_embedding_generator.config.review_embedding_property_name
        })
        
        print(f"Graph created: {result}")
        return result
    
    def create_graph_projection_production(self):
        """
        Create graph projection for production (all data).
        Rating is used as edge weight to influence FastRP propagation.
        """
        
        node_query = f"""
            MATCH (n)
            WHERE n:User OR n:Product OR n:Review
            RETURN id(n) AS id, 
                   labels(n) AS labels,
                   n.{self.semantic_embedding_generator.config.review_embedding_property_name} AS {self.semantic_embedding_generator.config.review_embedding_property_name}
        """
        
        # Rating as edge weight - higher rated reviews have stronger influence
        rel_query = """
            MATCH (u:User)-[:WROTE]->(r:Review)-[:ABOUT]->(p:Product)
            RETURN id(u) AS source, id(r) AS target, r.rating AS weight, 'WROTE' AS type
            
            UNION ALL
            
            MATCH (u:User)-[:WROTE]->(r:Review)-[:ABOUT]->(p:Product)
            RETURN id(r) AS source, id(p) AS target, r.rating AS weight, 'ABOUT' AS type
        """
        
        create_query = """
        CALL gds.graph.project.cypher(
                $graph_name,
                $node_query,
                $rel_query
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        print("Creating enhanced graph projection (production)...")
        
        result = self.db.execute_query(create_query, {
            "graph_name":  self.graph_name,
            "node_query": node_query,
            "rel_query": rel_query,
            "semantic_embedding_name": self.semantic_embedding_generator.config.review_embedding_property_name
        })
        
        print(f"Graph created: {result}")
        return result
        
    def generate_enhanced_fastrp_embeddings(self):
        """
        Generate FastRP embeddings that incorporate:
        - Review semantic embeddings (via featureProperties)
        - Rating as edge weight (via relationshipWeightProperty)
        
        Higher-rated reviews will have more influence on the embedding.
        """
        print("Generating FastRP embeddings with review semantics + rating weights...")
        
        # FastRP with node properties (semantic embeddings) AND relationship weights (ratings)
        query="""
        CALL gds.fastRP.mutate(
                $graph_name,
                {
                    mutateProperty: 'enhanced_fastrp_embedding',    // writing to new property - similarities will be based on this property
                    embeddingDimension: $dimensions,
                    iterationWeights: $weights,
                    randomSeed: $random_seed,
                    relationshipWeightProperty: 'weight',
                    featureProperties: [$semantic_embedding_name],
                    propertyRatio: $property_ratio,
                    nodeSelfInfluence: $self_influence
                }
            )
        YIELD nodeCount, nodePropertiesWritten, configuration
        RETURN nodeCount, nodePropertiesWritten, configuration
        """
        result =  self.db.execute_query(query, {
            "graph_name": self.graph_name,
            "dimensions": self.config.embedding_dimensions,
            "weights": self.config.iteration_weights,
            "random_seed": self.config.random_seed,
            "property_ratio": self.config.property_ratio,
            "self_influence": self.config.self_influence,
            "semantic_embedding_name": self.semantic_embedding_generator.config.review_embedding_property_name
        })
        
        print(f"FastRP embeddings generated: \n{result}")
        return result
    
    def setup_projection(self):
        """Full pipeline to generate projection and run fastRP."""
        print("Creating graph projection...")
        self.drop_graph_projection()
        res_creation = None
        if self.for_production:
            res_creation = self.create_graph_projection_production()
        else:
            res_creation = self.create_graph_projection_training()
        print(res_creation)
        
        print("Generating FastRP embeddings...")
        res_generation = self.generate_enhanced_fastrp_embeddings()
        print(res_generation)
        print("FastRP embeddings ready!")
    
    def run_knn(self):
        """Run KNN to find similar users based on enhanced embeddings."""
        print("Cleaning old SIMILAR_ENHANCED relationships...")
        self.db.execute_query("MATCH ()-[r:SIMILAR_ENHANCED]->() DELETE r")
        
        print("Running KNN on enhanced embeddings to write SIMILAR_ENHANCED relationships...")
        knn_query = """
        CALL gds.knn. write(
                $graph_name,
                {
                    nodeLabels: ['User'],
                    nodeProperties: ['enhanced_fastrp_embedding'],
                    writeRelationshipType: 'SIMILAR_ENHANCED',
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
        result = self.db.execute_query(knn_query, {
            "graph_name": self.graph_name,
            "sample_rate": self.config.review_sample_rate,
            "top_k": self.config.review_top_k
            })
        
        print(f"KNN complete: {result}")
        return result

    # =========================================================================
    
    def recommend_production(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate recommendations for a user (production mode)."""
        query = """
            MATCH (me:User {user_id: $user_id})-[s:SIMILAR_ENHANCED]-(similar:User)
            MATCH (similar)-[r:RATED]->(product:Product)
            WHERE NOT EXISTS { (me)-[:RATED]->(product) }
            
            WITH product,
                 SUM(s.score * r.rating) AS weighted_sum,
                 SUM(s.score) AS similarity_sum,
                 COUNT(similar) AS similar_users_count
            
            RETURN product.parent_asin AS parent_asin,
                   product.title AS title,
                   product.images[0] as image_representative,
                   product.average_rating AS average_rating,
                   weighted_sum / similarity_sum AS predicted_score,
                   similar_users_count
            ORDER BY predicted_score DESC
            LIMIT 10
        """
        
        return self.db.execute_query(query, {"user_id":  user_id})
    
    def recommend_training(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate recommendations using only training data."""
        query = """
            MATCH (me: User {user_id: $user_id})-[s:SIMILAR_ENHANCED]-(similar:User)
            MATCH (similar)-[r:RATED {split: 'train'}]->(product:Product)
            WHERE NOT EXISTS { (me)-[:RATED {split: 'train'}]->(product) }
            
            WITH product,
                 SUM(s.score * r. rating) AS weighted_sum,
                 SUM(s. score) AS similarity_sum,
                 COUNT(similar) AS similar_users_count
            
            RETURN product.parent_asin AS parent_asin,
                   product.title AS title,
                   weighted_sum / similarity_sum AS predicted_score,
                   similar_users_count
            ORDER BY predicted_score DESC
            LIMIT 10
        """
        
        return self.db. execute_query(query, {"user_id": user_id})
    
    def evaluate_performance(self, test_users: List[str]) -> Dict[str, float]:
        """Evaluate using Leave-One-Out method."""
        
        # Setup for evaluation (training mode)
        self.run_knn()
        
        hits = 0
        reciprocal_rank_sum = 0
        users_evaluated = 0

        print(f"Evaluating Enhanced Model-Based on {len(test_users)} users...")

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