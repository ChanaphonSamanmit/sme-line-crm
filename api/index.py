import os
import sys

# Make sure app/ modules are importable from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Response
from app.routers import line_bot, analytics, qr_point, product, upload
from app.config import settings

app = FastAPI(title="SME LINE CRM", version="2.0.0")

# Static files are served by Vercel CDN from /public directory.
# No StaticFiles mount needed here.

app.include_router(line_bot.router)
app.include_router(qr_point.router,  prefix="/api/v1/qr")
app.include_router(product.router,   prefix="/api/v1/product")
app.include_router(upload.router,    prefix="/api/v1/upload")
app.include_router(analytics.router, prefix="/api/v1/analytics")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "SME LINE CRM", "version": "2.0.0"}

@app.get("/api/v1/config")
def get_config():
    return {
        "liff_id":     settings.LIFF_ID,
        "merchant_id": settings.MERCHANT_ID
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")
