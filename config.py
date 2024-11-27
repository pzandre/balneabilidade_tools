import os

DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_LATEST_KEY = os.getenv("SUPABASE_LATEST_KEY", "latest.pgdump")
SUPABASE_LATEST_BUCKET = os.getenv("SUPABASE_LATEST_BUCKET")
SUPABASE_HISTORY_BUCKET = os.getenv("SUPABASE_HISTORY_BUCKET")
BACKUP_DIR = "/tmp"
MAX_BACKUP_QTY = int(os.getenv("MAX_BACKUP_QTY", 10))
