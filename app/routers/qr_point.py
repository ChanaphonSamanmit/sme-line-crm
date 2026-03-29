from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import CartItem, GenerateQRRequest, ClaimPointRequest


router = APIRouter()


@router.post("/generate")
async def generate_qr(data: GenerateQRRequest):
    try:
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
        
        receipt_id = "RCP-" + tx_id[:8].upper()
        supabase.table("member_transactions").update({
            "receipt_id": receipt_id
        }).eq("id", tx_id).execute()


        return {"status": "ok", "qr_id": tx_id, "receipt_id": receipt_id}


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
                 return {"status": "error", "message": "คุณสะสมยอดนี้ไปแล้วครับ"}
            else:
                 return {"status": "error", "message": "รายการนี้ถูกใช้สิทธิ์ไปแล้ว"}


        # 3. 🟢 แก้บัค: อัปเดต/สร้างข้อมูลสมาชิกแบบเซฟๆ (แทนการใช้ Upsert ที่ชอบบัค)
        member_check = supabase.table("members").select("id").eq("merchant_id", record['merchant_id']).eq("line_user_id", data.line_user_id).execute()
        
        if member_check.data:
            # ถ้ามีประวัติอยู่แล้ว ให้อัปเดตชื่อกับรูป
            supabase.table("members").update({
                "display_name": data.display_name,
                "picture_url": data.picture_url
            }).eq("id", member_check.data[0]['id']).execute()
        else:
            # ถ้าเป็นลูกค้าใหม่ ให้สร้าง Record ใหม่
            supabase.table("members").insert({
                "merchant_id": record['merchant_id'],
                "line_user_id": data.line_user_id,
                "display_name": data.display_name,
                "picture_url": data.picture_url
            }).execute()


        # 4. บันทึกความเป็นเจ้าของบิล
        supabase.table("member_transactions").update({
            "line_user_id": data.line_user_id,
            "customer_name": data.display_name,
            "customer_picture": data.picture_url,
            "status": "claimed"
        }).eq("id", data.qr_id).execute()


        return {"status": "success", "amount": record['amount'], "message": f"ขอบคุณครับคุณ {data.display_name}!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/info/{qr_id}")
async def get_qr_info(qr_id: str):
    try:
        res = supabase.table("member_transactions") \
            .select("id, amount, receipt_id, status") \
            .eq("id", qr_id) \
            .execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="ไม่พบรายการ")
        row = res.data[0]
        if row["status"] == "claimed":
            raise HTTPException(status_code=410, detail="รายการนี้ถูกสแกนไปแล้ว")
        return {"amount": row["amount"], "receipt_id": row["receipt_id"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
