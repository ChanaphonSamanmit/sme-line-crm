from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import supabase

router = APIRouter()

class ProductModel(BaseModel):
    merchant_id: str
    name: str
    price: float
    cost_price: float = 0
    image_url: Optional[str] = ""

@router.get("/list/{merchant_id}")
async def get_products(merchant_id: str):
    # ดึงสินค้าทั้งหมดของร้าน
    res = supabase.table("products").select("*").eq("merchant_id", merchant_id).eq("is_active", "true").execute()
    return res.data

@router.post("/add")
async def add_product(data: ProductModel):
    try:
        supabase.table("products").insert({
            "merchant_id": data.merchant_id,
            "name": data.name,
            "price": data.price,
            "cost_price": data.cost_price,
            "image_url": data.image_url
        }).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{product_id}")
async def delete_product(product_id: str):
    # ไม่ลบจริง แค่ซ่อน (Soft Delete) เพื่อรักษาประวัติการขาย
    supabase.table("products").update({"is_active": "false"}).eq("id", product_id).execute()
    return {"status": "ok"}