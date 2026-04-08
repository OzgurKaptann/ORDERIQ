import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import analytics, auth, catalog, modifiers, onboarding, orders, public, qr

app = FastAPI(title="OrderIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production via env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve QR images and other media
os.makedirs(f"{settings.MEDIA_DIR}/qr", exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# Routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(catalog.router)
app.include_router(modifiers.router)
app.include_router(public.router)
app.include_router(orders.router)
app.include_router(qr.router)
app.include_router(analytics.router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
