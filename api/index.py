import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Response

app = FastAPI()

_import_error = None

try:
    from app.config import settings
    from app.database import supabase
    from app.routers import line_bot, analytics, qr_point, product, upload

    app.include_router(line_bot.router)
    app.include_router(qr_point.router,  prefix="/api/v1/qr")
    app.include_router(product.router,   prefix="/api/v1/product")
    app.include_router(upload.router,    prefix="/api/v1/upload")
    app.include_router(analytics.router, prefix="/api/v1/analytics")

except Exception as e:
    _import_error = traceback.format_exc()


@app.get("/")
def health_check():
    if _import_error:
        return {"status": "error", "detail": _import_error}
    return {"status": "ok", "service": "SME LINE CRM", "version": "2.0.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")
