import os
from supabase import create_client, Client
from dotenv import load_dotenv
import psycopg2

# Chargement des variables d'environnement
load_dotenv()

url: str | None = os.getenv('SUPABASE_URL')
key: str | None = os.getenv('SUPABASE_KEY')
db_url: str | None = os.getenv('SUPABASE_DB_URL')

if not url or not key or not db_url:
    raise ValueError("Les variables SUPABASE_URL et SUPABASE_KEY sont introuvables.")

def get_supabase_client() -> Client:
    return create_client(url, key)

def get_connection_postgres():
    return psycopg2.connect(db_url)
