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
    try:
        # รองรับทั้ง boolean และ string "true"
        res = supabase.table("products").select("*").eq("merchant_id", merchant_id).execute()
        # Filter ที่ is_active ไม่ใช่ False/false/"false"
        data = [p for p in res.data if str(p.get("is_active", "true")).lower() not in ("false", "0")]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add")
async def add_product(data: ProductModel):
    try:
        res = supabase.table("products").insert({
            "merchant_id": data.merchant_id,
            "name": data.name,
            "price": data.price,
            "cost_price": data.cost_price,
            "image_url": data.image_url,
            "is_active": True
        }).execute()
        return {"status": "ok", "id": res.data[0]["id"] if res.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{product_id}")
async def delete_product(product_id: str):
    try:
        # Soft Delete — ไม่ลบจริง เพื่อรักษาประวัติการขาย
        supabase.table("products").update({"is_active": False}).eq("id", product_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))