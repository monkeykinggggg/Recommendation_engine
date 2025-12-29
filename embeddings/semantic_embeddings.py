from typing import List
from database.connection import Neo4jConnection
from config.settings import EmbeddingConfig
from sentence_transformers import SentenceTransformer

class SemanticEmbeddingGenerator:
    """Generate and manage semantic embeddings for products in Neo4j."""

    def __init__(self, db: Neo4jConnection, config: EmbeddingConfig = None):
        self.db = db
        self.config = config or EmbeddingConfig()
        self.model = None
        
    def _load_model(self):
        """Lazy load the sentence transformer model"""
        if self.model is None:
            try:
                print(f"Loading embedding model: {self.config.sbert_model_name}...")
                self.model = SentenceTransformer(self.config.sbert_model_name)
                print("Model loaded successfully!")
            except ImportError: 
                raise ImportError(
                    "sentence-transformers not installed."
                )
        return self.model
    
    def embed_text(self, text:  str) -> List[float]: 
        """Generate embedding for a single text."""
        self._load_model()
        return self.model.encode(text, normalize_embeddings=True).tolist()  # beacuse we get tensor as a result
    
    def embed_batch(self, texts:  List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        self._load_model()
        return self.model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        ).tolist()

    def prepare_product_text(self,title:  str, description:  List[str], features: List[str], store: str) -> str:
        """
        Combine product text fields into a single string for embedding. 
        
        Args:
            title: Product title (str)
            description: List of description paragraphs (List[str])
            features: List of product features (List[str])
            store: Brand/store name (str)
        
        Returns:
            Combined text string for embedding
        """
        parts = []
        
        if title: 
            parts.append(f"Product: {title}")
        
        if store:
            parts.append(f"Brand: {store}")
        
        if features and len(features) > 0:
            feature_text = " | ". join(features)
            parts.append(f"Features: {feature_text}")
        
        if description and len(description) > 0:
            desc_text = " ". join(description)
            parts.append(f"Description:  {desc_text}")
        
        return " ".join(parts)
    
    def _store_embeddings(self, asins: List[str], embeddings: List[List[float]]):
        """Store embeddings in Neo4j in batches."""
        print("Storing embeddings in Neo4j...")
        
        store_batch_size = 100
        
        for i in range(0, len(asins), store_batch_size):
            batch_asins = asins[i:i + store_batch_size]
            batch_embeddings = embeddings[i:i + store_batch_size]
            
            # funkcja SET w Neo4j nadpisuje istniejace wlasciwosci, jesli juz istnieja 
            self.db.execute_query(f"""
                UNWIND $batch AS item
                MATCH (p:Product {{parent_asin: item.parent_asin}})
                SET p.{self.config.embedding_property_name} = item.embedding
            """, {
                "batch": [
                    {"parent_asin": asin, "embedding": emb}
                    for asin, emb in zip(batch_asins, batch_embeddings)
                ]
            })
            
            print(f"  Stored {min(i + store_batch_size, len(asins))}/{len(asins)}")
        
        print("All embeddings stored!")
    
    def generate_product_embeddings(self) -> int:
        """
        Generate semantic embeddings for all products and store in Neo4j. 
        Returns the number of products embedded.
        """
        print("Fetching products from database...")
        
        # dla produktów, które nie mają jeszcze embeddingu, zapisujemy
        products = self.db.execute_query(f"""
            MATCH (p:Product)
            WHERE p.{self.config.embedding_property_name} IS NULL
            RETURN p.parent_asin AS parent_asin,
                   p.title AS title,
                   p.description AS description,
                   p.features AS features,
                   p.store AS store
        """)
        if len(products) == 0:
            print("All products already have embeddings.")
            return 0
    
        print(f"Found {len(products)} products to embed.")
        
        texts = []
        asins = []
        
        for prod in products:
            # Fields come directly from Neo4j in correct types: 
            # - title: str (or None)
            # - store: str (or None)
            # - description: List[str] (or None/empty)
            # - features: List[str] (or None/empty)
            
            text = self.prepare_product_text(
                title=prod.get('title') or '',
                description=prod.get('description') or [],
                features=prod.get('features') or [],
                store=prod.get('store') or ''
            )
            #print(text)
            texts.append(text)
            asins.append(prod['parent_asin'])
        
        #print(texts)
        #print(asins)
        print("Generating embeddings...")
        embeddings = self.embed_batch(texts)
        
        self._store_embeddings(asins, embeddings)
        
        print(f"Successfully embedded {len(asins)} products!")
        return len(asins)
    
    def create_vector_index(self):
        """Create Neo4j vector index for fast similarity search."""
        print(f"Creating vector index for '{self.config.embedding_property_name}' property in Product nodes ...")
        
        self.db.execute_query(f"""
            CREATE VECTOR INDEX {self.config.vector_index_name} IF NOT EXISTS
            FOR (p:Product) ON (p.{self.config.embedding_property_name})
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {self.config.embedding_dim},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
        """)
        
        print("Vector index created!")
        
    def drop_vector_index(self):
        """Drop the vector index if it exists."""
        try:
            self.db.execute_query(f"""
                DROP INDEX {self.config.vector_index_name} IF EXISTS
            """)
            print(f"Vector index '{self.config.vector_index_name}' dropped.")
        except Exception as e:
            print(f"Could not drop index: {e}")
            
            
    