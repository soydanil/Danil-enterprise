import uvicorn
from fastapi import FastAPI
from src.api.v1 import router as api_v1_router
from src.core.config import configure_cors

from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Apply CORS configuration
configure_cors(app)

# Include routers
app.include_router(api_v1_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
