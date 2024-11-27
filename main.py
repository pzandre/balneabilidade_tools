import os

from fastapi import FastAPI, Security
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader

from schemas import RestorePayload
from supabase_tools import initiate_backup_process, initiate_restore_process

app = FastAPI(
    debug=False,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)


def validate_api_key(
    api_key: str = Security(
        APIKeyHeader(name="X-API-Key", scheme_name="API key", auto_error=True)
    )
):
    if api_key not in os.environ.get("API_KEYS", "").split(","):
        raise HTTPException(
            status_code=403, detail={"success": False, "error": "Invalid API key"}
        )
    return True


@app.post("/management/initiate_backup_process")
async def initiate_backup(api_key: bool = Security(validate_api_key)):
    try:
        initiate_backup_process()
        return {"detail": {"success": True, "error": ""}}
    except Exception as e:
        return {"detail": {"success": False, "error": str(e)}}


@app.post("/management/initiate_restore_process")
async def initiate_restore(
    restore_info: RestorePayload, api_key=Security(validate_api_key)
):
    try:
        initiate_restore_process(restore_info.key, restore_info.bucket_name)
        return {"detail": {"success": True, "error": ""}}
    except Exception as e:
        return {"detail": {"success": False, "error": str(e)}}
