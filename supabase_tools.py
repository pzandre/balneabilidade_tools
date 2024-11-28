import concurrent.futures
import logging
import os
import subprocess
from datetime import datetime

from supabase import Client, create_client

from config import (
    BACKUP_DIR,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    MAX_BACKUP_QTY,
    SUPABASE_HISTORY_BUCKET,
    SUPABASE_KEY,
    SUPABASE_LATEST_BUCKET,
    SUPABASE_LATEST_KEY,
    SUPABASE_URL,
)


def upload_to_supabase(
    supabase_client: Client, file_path: str, key: str, bucket_name: str
):
    with open(file_path, "rb") as f:
        supabase_client.storage.from_(bucket_name).upload(
            file=f,
            path=key,
            file_options={"cache-control": "3600", "upsert": "true"},
        )


def perform_database_restore(backup_file: bytes) -> bool:
    """
    Perform PostgreSQL database restore using pg_restore.

    Returns:
    - Tuple (success, backup_file_path)
    """

    pg_restore_command = [
        "pg_restore",
        "-h",
        DB_HOST,
        "-p",
        DB_PORT,
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
        "-v",
        "-c",
        "-1",
        "-F",
        "c",
        "--if-exists",
    ]

    try:
        pg_env = os.environ.copy()
        pg_env["PGPASSWORD"] = DB_PASSWORD

        result = subprocess.run(
            pg_restore_command,
            env=pg_env,
            input=backup_file,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logging.info(f"Restore of database {DB_NAME} completed successfully")
            return True
        else:
            logging.error(f"Error: Restore of database {DB_NAME} failed")
            logging.error(f"Error output: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing pg_restore: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during restore: {e}")
        return False


def perform_database_dump(backup_file: str) -> bool:
    """
    Perform PostgreSQL database dump using pg_dump.

    Returns:
    - Tuple (success, backup_file_path)
    """

    pg_dump_command = [
        "pg_dump",
        "-h",
        DB_HOST,
        "-p",
        DB_PORT,
        "-U",
        DB_USER,
        "-F",
        "c",
        "--clean",
        "--if-exists",
        "-b",
        "-v",
        "-f",
        backup_file,
        DB_NAME,
    ]

    try:
        pg_env = os.environ.copy()
        pg_env["PGPASSWORD"] = DB_PASSWORD

        result = subprocess.run(
            pg_dump_command, env=pg_env, capture_output=True, text=True
        )

        if result.returncode == 0:
            logging.info(f"Backup of database {DB_NAME} completed successfully")
            return True
        else:
            logging.error(f"Error: Backup of database {DB_NAME} failed")
            logging.error(f"Error output: {result.stderr}")
            return False

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing pg_dump: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during backup: {e}")
        return False


def clean_historic_bucket(supabase_client: Client):
    response: list = supabase_client.storage.from_(SUPABASE_HISTORY_BUCKET).list(
        "folder",
        {
            "limit": 20,
            "offset": 0,
            "sortBy": {"column": "created_at", "order": "desc"},
        },
    )
    if len(response) > MAX_BACKUP_QTY:
        files_to_delete = response[MAX_BACKUP_QTY:]
        supabase_client.storage.from_(SUPABASE_HISTORY_BUCKET).remove(files_to_delete)


def initiate_backup_process():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_{timestamp}.pgdump")

    backup_success = perform_database_dump(backup_file)

    if not backup_success:
        raise Exception("Backup failed")

    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                upload_to_supabase,
                supabase_client,
                backup_file,
                SUPABASE_LATEST_KEY,
                SUPABASE_LATEST_BUCKET,
            ),
            executor.submit(
                upload_to_supabase,
                supabase_client,
                backup_file,
                f"{DB_NAME}_{timestamp}.pgdump",
                SUPABASE_HISTORY_BUCKET,
            ),
        ]
        concurrent.futures.wait(futures)
    clean_historic_bucket(supabase_client)


def get_restore_file_from_supabase(key: str, bucket_name: str) -> bytes:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client.storage.from_(bucket_name).download(key)


def initiate_restore_process(
    key: str = SUPABASE_LATEST_KEY, bucket_name: str = SUPABASE_LATEST_BUCKET
):
    backup_file = get_restore_file_from_supabase(key, bucket_name)
    restore_success = perform_database_restore(backup_file)

    if not restore_success:
        raise Exception("Restore failed")
