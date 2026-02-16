from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# เพิ่ม upload ตรงนี้
from app.routers import line_bot, transaction, analytics, qr_point, product, upload 

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(line_bot.router)
app.include_router(transaction.router, prefix="/api/v1/transactions")
app.include_router(analytics.router, prefix="/api/v1/analytics")
app.include_router(qr_point.router, prefix="/api/v1/qr")
app.include_router(product.router, prefix="/api/v1/product")
app.include_router(upload.router, prefix="/api/v1/upload") # <--- ลงทะเบียนตรงนี้

@app.get("/")
def read_root():
    return {"status": "ok", "message": "POS V2 Ready"}