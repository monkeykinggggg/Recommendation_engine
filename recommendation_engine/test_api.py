from fastapi import FastAPI

app = FastAPI()

# run /docs endpoint in browser for SwaggerUI documentation
# run /redoc endpoint in browser for ReDoc documentation

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/users/{user_id}")
def get_user(user_id: str, limit: int = 10):
    return {"user_id": user_id, "limit": limit}