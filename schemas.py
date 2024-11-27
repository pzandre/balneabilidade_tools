from pydantic import BaseModel

from config import SUPABASE_LATEST_BUCKET, SUPABASE_LATEST_KEY


class RestorePayload(BaseModel):
    key: str = SUPABASE_LATEST_KEY
    bucket_name: str = SUPABASE_LATEST_BUCKET
