import config
from supabase import create_client

supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
