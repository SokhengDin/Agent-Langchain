from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.api.v1.router import router as router_v1
from app.api.v2.router import router as router_v2


from app.core.config import settings

from app import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    yield
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount template
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# API router
app.include_router(router_v1, prefix=settings.API_V1_STR)
app.include_router(router_v2, prefix="/api/v2")

# Chat UI route
@app.get("/")
async def chat_page(request: Request):
    return templates.TemplateResponse(
        "chat.html"
        , {"request": request}
    )

if __name__ == "__main__":
    import uvicorn
    from uvicorn.config import LOGGING_CONFIG


    LOGGING_CONFIG["handlers"] = {}
    LOGGING_CONFIG["loggers"] = {}

    logger.info("Starting application")
    uvicorn.run("main:app"
                , host  = "0.0.0.0"
                , port  = settings.PORT
                , reload= True
                , reload_dirs   = ["app"]
                , log_config    = None)