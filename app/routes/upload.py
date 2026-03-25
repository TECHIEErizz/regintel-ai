from fastapi import APIRouter, UploadFile, File
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"

# Ensure uploads folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-documents")
async def upload_documents(
    old_doc: UploadFile = File(...),
    new_doc: UploadFile = File(...)
):
    try:
        old_path = os.path.join(UPLOAD_DIR, old_doc.filename)
        new_path = os.path.join(UPLOAD_DIR, new_doc.filename)

        # Save old document
        with open(old_path, "wb") as buffer:
            shutil.copyfileobj(old_doc.file, buffer)

        # Save new document
        with open(new_path, "wb") as buffer:
            shutil.copyfileobj(new_doc.file, buffer)

        return {
            "message": "Files uploaded successfully",
            "old_file": old_path,
            "new_file": new_path
        }

    except Exception as e:
        return {"error": str(e)}