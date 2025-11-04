from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app import logger


router = APIRouter()


@router.get("/plots/{file_id}")
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
        if file_path.suffix.lower() in [".jpg", ".jpeg"]:
            media_type = "image/jpeg"
        elif file_path.suffix.lower() == ".svg":
            media_type = "image/svg+xml"

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


@router.get("/notebooks/{file_id}")
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
