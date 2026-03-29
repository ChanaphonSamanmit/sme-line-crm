from fastapi import FastAPI, Response 
from fastapi.staticfiles import StaticFiles
from app.routers import line_bot, analytics, qr_point, product, upload

app = FastAPI(title="POS Pro V2", version="2.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Core Modules
app.include_router(line_bot.router)
app.include_router(qr_point.router, prefix="/api/v1/qr")
app.include_router(product.router, prefix="/api/v1/product")
app.include_router(upload.router, prefix="/api/v1/upload")
app.include_router(analytics.router, prefix="/api/v1/analytics")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "POS Pro V2 Ready 🚀"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")