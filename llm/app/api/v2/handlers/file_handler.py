from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app import logger


router = APIRouter()

ALLOWED_DIRECTORIES = {
    "plots"     : Path("output/plots"),
    "notebooks" : Path("output/notebooks"),
    "uploads"   : Path("uploads/images"),
}

MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".html": "text/html",
    ".pdf": "application/pdf",
    ".webp": "image/webp",
    ".ipynb": "application/x-ipynb+json",
    ".json": "application/json",
    ".csv": "text/csv",
    ".txt": "text/plain",
}


@router.get("/plots/{file_id}", deprecated=True)
async def get_plot(file_id: str):
    try:
        if ".." in file_id or "/" in file_id or "\\" in file_id:
            raise HTTPException(status_code=400, detail="Invalid file ID")

        plots_dir   = Path("output/plots").resolve()
        file_path   = plots_dir / file_id

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Plot file not found: {file_id}")

        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file path")

        try:
            file_path.resolve().relative_to(plots_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")

        logger.info(f"Serving plot file: {file_path}")

        media_type = "image/png"
        ext = file_path.suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            media_type = "image/jpeg"
        elif ext == ".svg":
            media_type = "image/svg+xml"
        elif ext == ".html":
            media_type = "text/html"
        elif ext == ".pdf":
            media_type = "application/pdf"

        return FileResponse(
            path        = str(file_path)
            , media_type= media_type
            , filename  = file_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving plot file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")


@router.get("/uploads/images/{file_id}")
async def get_uploaded_image(file_id: str):
    try:
        if ".." in file_id or "/" in file_id or "\\" in file_id:
            raise HTTPException(status_code=400, detail="Invalid file ID")

        uploads_dir = Path("uploads/images").resolve()
        file_path   = uploads_dir / file_id

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {file_id}")

        try:
            file_path.resolve().relative_to(uploads_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")

        logger.info(f"Serving uploaded image: {file_path}")

        media_type = "image/png"
        ext = file_path.suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            media_type = "image/jpeg"
        elif ext == ".webp":
            media_type = "image/webp"

        return FileResponse(
            path        = str(file_path)
            , media_type= media_type
            , filename  = file_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")


@router.get("/notebooks/{file_id}", deprecated=True)
async def get_notebook(file_id: str):
    try:
        if ".." in file_id or "/" in file_id or "\\" in file_id:
            raise HTTPException(status_code=400, detail="Invalid file ID")

        notebooks_dir = Path("output/notebooks").resolve()
        file_path = notebooks_dir / file_id

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Notebook not found: {file_id}")

        if not file_path.suffix.lower() == ".ipynb":
            raise HTTPException(status_code=400, detail="Invalid file type")

        try:
            file_path.resolve().relative_to(notebooks_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")

        logger.info(f"Serving notebook file: {file_path}")

        return FileResponse(
            path=str(file_path),
            media_type="application/x-ipynb+json",
            filename=file_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving notebook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")


@router.get("/{directory}/{file_id}")
async def get_ds_file(directory: str, file_id: str):
    """
    Unified endpoint to serve any DS agent generated file.

    Supports:
    - /plots/{file_id} - Images (PNG, JPG, SVG), HTML visualizations, PDFs
    - /notebooks/{file_id} - Jupyter notebooks (.ipynb)
    - /uploads/{file_id} - Uploaded images
    """
    try:
        if ".." in file_id or "/" in file_id or "\\" in file_id:
            raise HTTPException(status_code=400, detail="Invalid file ID")

        if directory not in ALLOWED_DIRECTORIES:
            raise HTTPException(status_code=400, detail=f"Invalid directory: {directory}")

        base_dir    = ALLOWED_DIRECTORIES[directory].resolve()
        file_path   = base_dir / file_id

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Invalid file path")

        try:
            file_path.resolve().relative_to(base_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid file path")

        ext         = file_path.suffix.lower()
        media_type  = MEDIA_TYPES.get(ext, "application/octet-stream")

        return FileResponse(
            path        = str(file_path)
            , media_type= media_type
            , filename  = file_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file from {directory}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")
