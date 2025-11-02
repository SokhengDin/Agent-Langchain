import uuid
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app import logger


router = APIRouter()


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image file and save to disk.
    Returns the file path for use with vision tools.
    """
    try:
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400
                , detail=f"Unsupported format. Allowed: {', '.join(allowed_extensions)}"
            )

        upload_dir = Path("uploads/images")
        upload_dir.mkdir(parents=True, exist_ok=True)

        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id   = str(uuid.uuid4())[:8]
        filename    = f"{timestamp}_{unique_id}{file_ext}"
        file_path   = upload_dir / filename

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Image uploaded: {file_path}")

        return JSONResponse({
            "status"    : "success"
            , "message" : "Image uploaded successfully"
            , "data"    : {
                "filename"  : filename
                , "path"    : str(file_path)
                , "size"    : len(content)
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF file and save to disk.
    Returns the file path for use with RAG tools.
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400
                , detail="Only PDF files are allowed"
            )

        upload_dir = Path("uploads/documents")
        upload_dir.mkdir(parents=True, exist_ok=True)

        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id   = str(uuid.uuid4())[:8]
        filename    = f"{timestamp}_{unique_id}.pdf"
        file_path   = upload_dir / filename

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"PDF uploaded: {file_path}")

        return JSONResponse({
            "status"    : "success"
            , "message" : "PDF uploaded successfully"
            , "data"    : {
                "filename"  : filename
                , "path"    : str(file_path)
                , "size"    : len(content)
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload any file (auto-detects image or PDF).
    Returns the file path for use with appropriate tools.
    """
    try:
        file_ext = Path(file.filename).suffix.lower()

        image_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        if file_ext in image_extensions:
            return await upload_image(file)
        elif file_ext == ".pdf":
            return await upload_pdf(file)
        else:
            raise HTTPException(
                status_code=400
                , detail=f"Unsupported file type: {file_ext}. Supported: images (jpg, png, webp) and PDF"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
