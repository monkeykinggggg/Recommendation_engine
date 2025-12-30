from database.connection import Neo4jConnection
from config.settings import EmbeddingConfig

class GraphEmbeddingGenerator:
    """Generate and manage FastRP graph embeddings in Neo4j for model based recommender"""
    
    def __init__(self, db: Neo4jConnection, config: EmbeddingConfig = None, for_production:bool=True):
        self.db = db
        self.config = config or EmbeddingConfig()
        self.graph_name = "prod_fastrp" if for_production else "train_fastrp"
        self.for_production = for_production
    
    def drop_graph_projection(self):
        """Drop in-memory graph projection if it exists"""
        # Use Cypher query instead of self.gds (which doesn't exist)
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
            self.db.execute_query(drop_query, {"graph_name":  self.graph_name})
            print(f"Graph '{self.graph_name}' dropped.")
        else:
            print(f"Graph '{self.graph_name}' does not exist.  No action taken.")
    
    def create_graph_projection_training(self):
        """Create in-memory training graph projection using Cypher Projection for GDS algorithms"""
        
        node_query = "MATCH (n) WHERE n:User OR n:Product RETURN id(n) AS id, labels(n) AS labels"
        rel_query = """
        MATCH (n:User)-[r:RATED]->(m:Product)
        WHERE r.split = "train"
        RETURN id(n) AS source, id(m) AS target, r.rating AS rating, 'RATED' AS type
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
        return self.db.execute_query(create_query, {
            "graph_name": self.graph_name,
            "node_query": node_query,
            "rel_query": rel_query
        })
        
    
    def create_graph_projection_production(self):
        """Create in-memory graph projection for GDS algorithms"""
        
        create_query ="""
        CALL gds.graph.project(
            $graph_name,
            ['User', 'Product'],
            {
                RATED: {
                    type: 'RATED',
                    properties: ['rating'],
                    orientation: 'UNDIRECTED'
                }
            }
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """
        # tworzy sie dwa razy wiecej relacji poniewaz orientacja jest UNDIRECTED, wezlow tyle co liczba produktow + liczba userow
        return self.db.execute_query(create_query, {"graph_name": self.graph_name})
    
    def generate_fastrp_embeddings(self):
        """Generate FastRP embeddings for users and products"""
        # writing only embeddings to User nodes on ouptut projection - less memory used
        query = """
        CALL gds.fastRP.mutate(
            $graph_name,
            {
                mutateProperty: 'fastrp_embedding',
                embeddingDimension: $dimensions,
                iterationWeights: $weights,
                randomSeed: $random_seed,
                relationshipWeightProperty: 'rating'
            }
        )
        YIELD nodeCount, nodePropertiesWritten, configuration
        RETURN nodeCount, nodePropertiesWritten, configuration
        """
        return self.db.execute_query(query, {
            "graph_name": self.graph_name,
            "dimensions": self.config.embedding_dimensions,
            "weights": self.config.iteration_weights,
            "random_seed": self.config.random_seed
        })
    
    
    def setup_embeddings(self):
        """Full pipeline to generate and store embeddings"""
        print("Creating graph projection...")
        self.drop_graph_projection()
        res_creation = None
        if self.for_production:
            res_creation = self.create_graph_projection_production()
        else:
            res_creation = self.create_graph_projection_training()
        print(res_creation)
        
        print("Generating FastRP embeddings...")
        res_generation = self.generate_fastrp_embeddings()
        print(res_generation)
        print("FastRP embeddings ready!")
        