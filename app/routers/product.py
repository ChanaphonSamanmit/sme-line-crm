"""
Product CRUD API
Author: Chanaphon (Backend Lead)
Endpoints: list, add, update, delete (soft)
"""
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import ProductCreate, ProductUpdate
 
router = APIRouter()
 
 
@router.get("/list/{merchant_id}")
async def get_products(merchant_id: str):
    """ดึงรายการสินค้าที่ยังใช้งานอยู่"""
    try:
        res  = supabase.table("products").select("*").eq("merchant_id", merchant_id).execute()
        data = [p for p in res.data if str(p.get("is_active", "true")).lower() not in ("false", "0")]
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.post("/add")
async def add_product(data: ProductCreate):
    """เพิ่มสินค้าใหม่"""
    try:
        res = supabase.table("products").insert({
            "merchant_id": data.merchant_id,
            "name":        data.name,
            "price":       data.price,
            "cost_price":  data.cost_price,
            "image_url":   data.image_url,
            "is_active":   True
        }).execute()
        return {"status": "ok", "id": res.data[0]["id"] if res.data else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.put("/update/{product_id}")
async def update_product(product_id: str, data: ProductUpdate):
    """อัปเดตข้อมูลสินค้า (เฉพาะ field ที่ส่งมา)"""
    try:
        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        if not payload:
            raise HTTPException(status_code=400, detail="ไม่มีข้อมูลที่จะอัปเดต")
        supabase.table("products").update(payload).eq("id", product_id).execute()
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.delete("/delete/{product_id}")
async def delete_product(product_id: str):
    """Soft Delete — ไม่ลบจริง เพื่อรักษาประวัติการขาย"""
    try:
        supabase.table("products").update({"is_active": False}).eq("id", product_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))