import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialize Supabase client
supabase: Optional[Client] = None

def get_supabase() -> Client:
    """Get or create a Supabase client instance."""
    global supabase
    if supabase is None:
        if not all([SUPABASE_URL, SUPABASE_KEY]):
            raise ValueError("Missing required Supabase environment variables")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
