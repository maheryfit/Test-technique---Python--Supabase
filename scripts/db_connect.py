import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_KEY')

if not url or not key:
    raise ValueError("Les variables SUPABASE_URL et SUPABASE_KEY sont introuvables.")

def get_supabase_client() -> Client:
    return create_client(url, key)
