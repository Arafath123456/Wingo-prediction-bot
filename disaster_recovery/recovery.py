import boto3
import subprocess
import os
from database.session import get_engine
from loguru import logger

def restore_database(backup_key: str):
    """Restore database from S3 backup"""
    # Download backup
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )
    
    s3_bucket = os.getenv("BACKUP_BUCKET", "wingo-backups")
    backup_file = f"/tmp/{os.path.basename(backup_key)}"
    
    s3.download_file(s3_bucket, backup_key, backup_file)
    
    # Get database connection
    engine = get_engine()
    db_url = engine.url
    
    # Terminate existing connections
    with engine.connect() as conn:
        conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_url.database}'
            AND pid <> pg_backend_pid();
        """))
    
    # Drop and recreate database
    subprocess.run(
        f"psql -h {db_url.host} -p {db_url.port} -U {db_url.username} -d postgres -c 'DROP DATABASE {db_url.database}'",
        shell=True, env={"PGPASSWORD": db_url.password}
    )
    
    subprocess.run(
        f"psql -h {db_url.host} -p {db_url.port} -U {db_url.username} -d postgres -c 'CREATE DATABASE {db_url.database}'",
        shell=True, env={"PGPASSWORD": db_url.password}
    )
    
    # Restore backup
    restore_cmd = f"pg_restore -d {db_url.database} -h {db_url.host} -p {db_url.port} -U {db_url.username} {backup_file}"
    subprocess.run(restore_cmd, shell=True, check=True, env={"PGPASSWORD": db_url.password})
    
    logger.success("Database restored successfully")
    return True