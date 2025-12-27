from database.connection import Neo4jConnection
from config.settings import EmbeddingConfig

class GraphEmbeddingGenerator:
    """Generate and manage FastRP graph embeddings in Neo4j"""
    
    def __init__(self, db: Neo4jConnection, config: EmbeddingConfig = None):
        self.db = db
        self.config = config or EmbeddingConfig()
    
    def create_graph_projection(self):
        """Create in-memory graph projection for GDS algorithms"""
        
        # Drop existing projection if exists
        drop_query = """
        CALL gds.graph. exists('recommendations') YIELD exists
        WITH exists WHERE exists
        CALL gds.graph. drop('recommendations') YIELD graphName
        RETURN graphName
        """
        try:
            self. db.execute_query(drop_query)
        except: 
            pass  # Projection doesn't exist
        
        # Create new projection
        create_query = """
        CALL gds.graph. project(
            'recommendations',
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
        return self.db.execute_query(create_query)
    
    def generate_fastrp_embeddings(self):
        """Generate FastRP embeddings for users and products"""
        
        query = """
        CALL gds.fastRP.mutate(
            'recommendations',
            {
                embeddingDimension: $dimensions,
                iterationWeights: $weights,
                mutateProperty: 'embedding',
                randomSeed: 42
            }
        )
        YIELD nodePropertiesWritten
        RETURN nodePropertiesWritten
        """
        return self. db.execute_query(query, {
            "dimensions": self.config.fastrp_dimensions,
            "weights": self.config.fastrp_iteration_weights
        })
    
    def write_embeddings_to_db(self):
        """Write embeddings from projection back to database"""
        
        query = """
        CALL gds.graph. nodeProperties. write(
            'recommendations',
            ['embedding']
        )
        YIELD propertiesWritten
        RETURN propertiesWritten
        """
        return self.db.execute_query(query)
    
    def setup_embeddings(self):
        """Full pipeline to generate and store embeddings"""
        print("Creating graph projection...")
        self.create_graph_projection()
        
        print("Generating FastRP embeddings...")
        self.generate_fastrp_embeddings()
        
        print("Writing embeddings to database...")
        self.write_embeddings_to_db()
        
        print("FastRP embeddings ready!")