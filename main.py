from fastapi import FastAPI

from schemas import RestorePayload
from supabase_tools import initiate_backup_process, initiate_restore_process

app = FastAPI(
    debug=False,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)


@app.post("/management/initiate_backup_process")
async def initiate_backup():
    try:
        initiate_backup_process()
        return {"detail": {"success": True, "error": ""}}
    except Exception as e:
        return {"detail": {"success": False, "error": str(e)}}


@app.post("/management/initiate_restore_process")
async def initiate_restore(restore_info: RestorePayload):
    try:
        initiate_restore_process(restore_info.key, restore_info.bucket_name)
        return {"detail": {"success": True, "error": ""}}
    except Exception as e:
        return {"detail": {"success": False, "error": str(e)}}
