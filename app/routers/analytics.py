from fastapi import APIRouter
from app.database import supabase
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/transactions/{merchant_id}")
async def get_transaction_history(merchant_id: str, date: str = None):
    """ใช้โดย admin.html เพื่อโหลดตารางยอดขายและคำนวณ Dashboard ด้วย JS"""
    try:
        query = supabase.table("member_transactions") \
            .select("*, transaction_items(product_id, quantity, price_at_sale, cost_at_sale, products(name))") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True) \
            .limit(100)

        if date:
            date_end = (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat()
            query = query.gte("created_at", date).lt("created_at", date_end)

        res = query.execute()
        return res.data
    except Exception as e:
        print(e)
        return []

@router.get("/member-summary/{line_user_id}")
async def get_member_summary(line_user_id: str, merchant_id: str):
    """ใช้โดย index.html สรุปข้อมูลสมาชิกรายบุคคล สำหรับหน้าสะสมแต้ม LIFF"""
    try:
        txs = supabase.table("member_transactions") \
            .select("amount, created_at, receipt_id, status") \
            .eq("merchant_id", merchant_id) \
            .eq("line_user_id", line_user_id) \
            .order("created_at", desc=True) \
            .execute()

        total_spent = sum(t['amount'] for t in txs.data)
        tx_count = len(txs.data)
        first_purchase = txs.data[-1]['created_at'] if txs.data else None

        return {
            "total_spent": total_spent,
            "tx_count": tx_count,
            "first_purchase": first_purchase,
            "recent_transactions": txs.data[:10]
        }
    except Exception as e:
        return {"total_spent": 0, "tx_count": 0, "first_purchase": None, "recent_transactions": []}