from fastapi.middleware.cors import CORSMiddleware

def configure_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Change this to specific domains in production
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
        allow_headers=["*"],
    )