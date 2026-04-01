import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from app.routers import line_bot, analytics, qr_point, product, upload
from app.config import settings

app = FastAPI(title="SME LINE CRM", version="2.0.0")

app.include_router(line_bot.router)
app.include_router(qr_point.router,  prefix="/api/v1/qr")
app.include_router(product.router,   prefix="/api/v1/product")
app.include_router(upload.router,    prefix="/api/v1/upload")
app.include_router(analytics.router, prefix="/api/v1/analytics")

@app.get("/admin")
async def admin_page():
    p = os.path.join(_ROOT, "public/static/admin/index.html")
    if not os.path.exists(p):
        # Debug: list what IS in the bundle
        files = []
        for root, dirs, filenames in os.walk(_ROOT):
            for f in filenames[:5]:
                files.append(os.path.relpath(os.path.join(root, f), _ROOT))
        return {"error": "file not found", "tried": p, "root": _ROOT, "sample_files": files[:20]}
    return FileResponse(p)

@app.get("/liff")
async def liff_page():
    p = os.path.join(_ROOT, "public/static/liff/index.html")
    if not os.path.exists(p):
        return {"error": "file not found", "tried": p}
    return FileResponse(p)

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
