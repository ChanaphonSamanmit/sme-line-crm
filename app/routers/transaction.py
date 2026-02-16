from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import supabase
from app.config import settings

router = APIRouter()

# กำหนดรูปแบบข้อมูลที่รับจากหน้าเว็บ
class TransactionRequest(BaseModel):
    receipt_id: str
    amount: float
    line_user_id: str
    merchant_id: str

@router.post("/scan")
async def scan_receipt(data: TransactionRequest):
    try:
        # 1. บันทึกธุรกรรมลงตาราง member_transactions
        # หมายเหตุ: ในขั้นตอนนี้เราสมมติว่ามี member_id และ merchant_id ที่ถูกต้องแล้ว
        insert_data = {
            "receipt_id": data.receipt_id,
            "amount": data.amount,
            "merchant_id": data.merchant_id,
            # ในระบบจริงต้องมีการ Query หา member_id จาก line_user_id ก่อน
        }
        
        result = supabase.table("member_transactions").insert(insert_data).execute()
        
        return {"status": "success", "message": "บันทึกแต้มสำเร็จ"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))