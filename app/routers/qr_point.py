from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import supabase

router = APIRouter()

# ... (ส่วน CartItem และ GenerateQRRequest เหมือนเดิม ไม่ต้องแก้) ...
class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    cost: float
    quantity: int

class GenerateQRRequest(BaseModel):
    merchant_id: str
    items: List[CartItem]
    total_amount: float
    discount: float = 0

@router.post("/generate")
async def generate_qr(data: GenerateQRRequest):
    try:
        # สร้าง Transaction (เหมือนเดิม)
        tx_res = supabase.table("member_transactions").insert({
            "merchant_id": data.merchant_id,
            "amount": data.total_amount,
            "discount_applied": data.discount,
            "receipt_id": "AUTO",
            "status": "pending"
        }).execute()
        
        tx_id = tx_res.data[0]['id']

        items_data = []
        for item in data.items:
            items_data.append({
                "transaction_id": tx_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_sale": item.price,
                "cost_at_sale": item.cost
            })
        
        if items_data:
            supabase.table("transaction_items").insert(items_data).execute()
        
        supabase.table("member_transactions").update({
            "receipt_id": "RCP-" + tx_id[:8].upper()
        }).eq("id", tx_id).execute()

        return {"status": "ok", "qr_id": tx_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
# 🔥 ส่วนที่แก้ใหม่: รับข้อมูล Profile ลูกค้าด้วย
# ---------------------------------------------------------
class ClaimPointRequest(BaseModel):
    line_user_id: str
    qr_id: str
    display_name: str  # เพิ่ม
    picture_url: str   # เพิ่ม

@router.post("/claim")
async def claim_point(data: ClaimPointRequest):
    try:
        # 1. เช็ครายการ
        check = supabase.table("member_transactions").select("*").eq("id", data.qr_id).execute()
        if not check.data: return {"status": "error", "message": "ไม่พบรายการ"}
        record = check.data[0]
        
        # 2. เช็คสิทธิ์
        if record['status'] == 'claimed' or record['line_user_id'] is not None:
            if record['line_user_id'] == data.line_user_id:
                 return {"status": "error", "message": "สะสมไปแล้วครับ"}
            else:
                 return {"status": "error", "message": "รายการนี้ถูกใช้สิทธิ์ไปแล้ว"}

        # 3. อัปเดต/สร้างข้อมูลสมาชิก (CRM)
        # ใช้ upsert เพื่อเก็บข้อมูลล่าสุดของลูกค้าคนนี้เสมอ
        supabase.table("members").upsert({
            "merchant_id": record['merchant_id'],
            "line_user_id": data.line_user_id,
            "display_name": data.display_name,
            "picture_url": data.picture_url
        }, on_conflict="merchant_id, line_user_id").execute()

        # 4. บันทึกความเป็นเจ้าของบิล (พร้อมชื่อแปะในบิลเลย ดูง่ายตอนทำ report)
        supabase.table("member_transactions").update({
            "line_user_id": data.line_user_id,
            "customer_name": data.display_name,   # บันทึกชื่อ
            "customer_picture": data.picture_url, # บันทึกรูป
            "status": "claimed"
        }).eq("id", data.qr_id).execute()

        return {"status": "success", "amount": record['amount'], "message": f"ขอบคุณครับคุณ {data.display_name}!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}