import os
import boto3
import datetime
from database.session import get_engine
from sqlalchemy import text
import subprocess
from loguru import logger

def backup_database():
    """Create database backup and upload to S3"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/wingo_backup_{timestamp}.sql"
    
    # Get database connection info
    engine = get_engine()
    db_url = engine.url
    
    # Create dump
    dump_cmd = f"pg_dump -Fc -d {db_url.database} -h {db_url.host} -p {db_url.port} -U {db_url.username} > {backup_file}"
    os.environ["PGPASSWORD"] = db_url.password
    subprocess.run(dump_cmd, shell=True, check=True)
    
    # Upload to S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )
    
    s3_bucket = os.getenv("BACKUP_BUCKET", "wingo-backups")
    s3_key = f"backups/{timestamp}.dump"
    
    s3.upload_file(backup_file, s3_bucket, s3_key)
    logger.success(f"Backup uploaded to s3://{s3_bucket}/{s3_key}")
    
    # Clean up
    os.remove(backup_file)
    
    return s3_key

def schedule_backups():
    """Schedule regular database backups"""
    import schedule
    import time
    
    # Daily full backup at 1 AM UTC
    schedule.every().day.at("01:00").do(backup_database)
    
    # Hourly differential backups (not implemented)
    
    while True:
        schedule.run_pending()
        time.sleep(60)