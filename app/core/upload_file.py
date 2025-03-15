import os
import uuid
import shutil
from fastapi import UploadFile, File
from app.configs.config import settings

def upload_file(file: UploadFile = File(...), path: str = "uploads"):
    # create path if not exit
    os.makedirs(os.path.join(settings.STATIC_FOLDER, path), exist_ok=True)

    # Save the file to a temporary location
    # temp_file_path = f"temp_{file.filename}"
    # with open(temp_file_path, "wb") as temp_file:
    #     shutil.copyfileobj(file.file, temp_file)

    # Generate a unique filename
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"

    # Upload the file to S3
    # s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    # bucket_name = settings.AWS_BUCKET_NAME
    # s3_key = f"uploads/{file.filename}"
    # s3_client.upload_file(temp_file_path, bucket_name, s3_key)
    # # Delete the temporary file
    # os.remove(temp_file_path)
    # return {"message": "File uploaded successfully"}

    # upload_to static folder
    file_path = os.path.join(settings.STATIC_FOLDER, path, unique_filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_path.replace('app/', "")