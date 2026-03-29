from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import line_bot, analytics, qr_point, product, upload


app = FastAPI(title="SME LINE CRM", version="2.0.0")


app.mount("/static", StaticFiles(directory="static"), name="static")


# API Routers
app.include_router(line_bot.router)
app.include_router(qr_point.router,  prefix="/api/v1/qr")
app.include_router(product.router,   prefix="/api/v1/product")
app.include_router(upload.router,    prefix="/api/v1/upload")
app.include_router(analytics.router, prefix="/api/v1/analytics")


# Page Routes
@app.get("/admin")
async def admin_page():
    return FileResponse("static/admin/index.html")


@app.get("/liff")
async def liff_page():
    return FileResponse("static/liff/index.html")


@app.get("/")
def health_check():
    return {"status": "ok", "service": "SME LINE CRM", "version": "2.0.0"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")
            