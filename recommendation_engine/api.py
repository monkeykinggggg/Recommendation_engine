from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel

from engine.config.settings import Neo4jConfig
from engine.database.connection import Neo4jConnection
from engine.recommenders.enhanced_model_based import EnhancedModelBasedRecommender
from engine.recommenders.content_based import ContentBasedRecommender


class ProductRecommendation(BaseModel):
    parent_asin: str
    title: Optional[str] = None
    image_representative: Optional[str] = None
    predicted_score: Optional[float] = None
    similarity_score: Optional[float] = None
    similar_users_count: Optional[int] = None

class RecommendationResponse(BaseModel):
    user_id: str
    algorithm: str
    recommendations: List[ProductRecommendation]


class AppState:
    db: Neo4jConnection = None
    enhanced_model_recommender: EnhancedModelBasedRecommender = None
    content_based_recommender: ContentBasedRecommender = None

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and recommenders on startup, cleanup on shutdown."""
    print("Starting up API...")
    db_config = Neo4jConfig()
    state.db = Neo4jConnection(db_config)
    
    print("Initializing Enhanced Model-Based Recommender...")
    state.enhanced_model_recommender = EnhancedModelBasedRecommender(state.db, for_production=True)
    state.enhanced_model_recommender.setup_projection()
    state.enhanced_model_recommender.run_knn()
    
    print("Initializing Content-Based Recommender...")
    state.content_based_recommender = ContentBasedRecommender(state.db)
    
    print("API ready!")
    
    yield
    
    print("Shutting down API...")
    if state.db:
        state.db.close()
    print("Database connection closed.")


app = FastAPI(
    title="Recommendation Engine API",
    description="REST API for product recommendations using Enhanced Model-Based and Content-Based algorithms and query search",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Recommendation Engine API is running"}


@app.get(
    "/recommendations/enhanced/{user_id}",
    response_model=RecommendationResponse,
    summary="Get Enhanced Model-Based Recommendations for User",
    description="Returns user-based product recommendations for a user using FastRP embeddings with review semantics and rating weights"
)
async def get_enhanced_recommendations(user_id: str):
    """
    Get recommendations from the Enhanced Model-Based recommender.
    
    This algorithm combines:
    - Graph structure (User-Review-Product relationships)
    - Review semantic embeddings
    - User similarity via KNN
    """
    try:
        recommendations = state.enhanced_model_recommender.recommend_production(user_id)
        # print(recommendations.__getitem__(0).get("image_representative"))
        if not recommendations:
            raise HTTPException(
                status_code=404, 
                detail=f"No recommendations found for user {user_id}. User may not exist or have no similar users."
            )
        return RecommendationResponse(
            user_id=user_id,
            algorithm=state.enhanced_model_recommender.get_name(),
            recommendations=[
                ProductRecommendation(
                    parent_asin=rec.get("parent_asin"),
                    title=rec.get("title"),
                    image_representative=rec.get("image_representative"),
                    predicted_score=rec.get("predicted_score"),
                    similar_users_count=rec.get("similar_users_count")
                )
                for rec in recommendations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/recommendations/content-based/{user_id}/{product_id}",
    response_model=RecommendationResponse,
    summary="Get Content-Based Recommendations for User and Product Viewed",
    description="Returns products similar to the specified product, excluding items the user has already rated"
)
async def get_content_based_recommendations(user_id: str, product_id: str):
    """
    Get recommendations from the Content-Based recommender.
    
    Returns products semantically similar to the specified product,
    useful for "Similar Products" or "You might also like" sections.
    """
    try:
        recommendations = state.content_based_recommender.recommend_production(user_id, product_id)
        # print(recommendations.__getitem__(0).get("image_representative"))
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No similar products found for product {product_id}. Product may not exist or have no embedding. Or User may not exist."
            )
        
        return RecommendationResponse(
            user_id=user_id,
            algorithm=state.content_based_recommender.get_name(),
            recommendations=[
                ProductRecommendation(
                    parent_asin=rec.get("parent_asin"),
                    title = rec.get("title"),
                    image_representative=rec.get("image_representative"),
                    similarity_score=rec.get("semantic_similarity")
                )
                for rec in recommendations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/search/{user_id}",
    response_model=RecommendationResponse,
    summary="Search Products by Query using Content-Based Recommender",
    description="Search for products using natural language query with semantic embeddings"
)
async def search_products(user_id: str, q:str = Query(..., min_length=1, description="Search query text")):
    """
    Search for products not rated by a user using semantic similarity.
    
    The query is embedded using the same model as product descriptions,
    allowing for natural language searches like "face cream".
    """
    try:
        # Use the content-based recommender's query search
        recommendations = state.content_based_recommender.recommend_by_query(q,user_id)
        print(recommendations.__getitem__(0).get("image_representative"))
        if not recommendations:
            raise HTTPException(
                status_code=404,
                detail=f"No similar products found for query '{q}'. Query may not match any products or User may not exist."
            )
        
        return RecommendationResponse(
            user_id=user_id,
            algorithm=state.content_based_recommender.get_name(),
            recommendations=[
                ProductRecommendation(
                    parent_asin=rec.get("parent_asin"),
                    title = rec.get("title"),
                    image_representative=rec.get("image_representative"),
                    similarity_score=rec.get("semantic_similarity")
                )
                for rec in recommendations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/users", 
    summary="Get All Users. Testing Purpose Only", 
    description="Returns list of 100 example user IDs in the system and the number of all users in db"
)
async def get_all_users():
    """Get all user IDs for testing purposes."""
    try:
        users = state.enhanced_model_recommender.get_all_users_ids()
        return {"count": len(users), "users": users[:100]} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
