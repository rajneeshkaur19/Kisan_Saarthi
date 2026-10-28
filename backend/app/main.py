import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    ),
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.database import init_db
from app.routers import (
    health,
    diagnose,
    prices,
    eligibility,
    chat,
    weather,
    gemini,
)

app = FastAPI(
    title="KisanSaarthi API",
    description=(
        "AI-powered agritech platform connecting crop health, "
        "market prices, and agricultural credit."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    print(f"[{settings.APP_NAME}] Initializing database tables...")
    init_db()
    print(f"[{settings.APP_NAME}] Backend initialized successfully.")


# Register API routers
app.include_router(health.router)
app.include_router(diagnose.router)
app.include_router(prices.router)
app.include_router(eligibility.router)
app.include_router(chat.router)
app.include_router(weather.router)
app.include_router(gemini.router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "tagline": "From Farm to Finance, with AI",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": [
            "GET /health",
            "POST /diagnose",
            "GET /prices",
            "POST /eligibility",
            "POST /checklist",
            "POST /chat",
            "GET /weather",
        ],
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"[API ERROR] {type(exc).__name__}: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": (
                    "An unexpected server error occurred. "
                    "Please contact KisanSaarthi support."
                ),
            },
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
