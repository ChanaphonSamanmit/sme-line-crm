"""
Analytics & Reporting API
Author: Chanaphon (Backend Lead)
Endpoints: transactions, summary, member-summary
"""
from fastapi import APIRouter
from app.database import supabase
from datetime import datetime, timedelta
 
router = APIRouter()
 
 
@router.get("/transactions/{merchant_id}")
async def get_transaction_history(merchant_id: str, date: str = None):
    """โหลดรายการทั้งหมดสำหรับ Admin Dashboard"""
    try:
        query = supabase.table("member_transactions") \
            .select("*, transaction_items(product_id, quantity, price_at_sale, cost_at_sale, products(name))") \
            .eq("merchant_id", merchant_id) \
            .order("created_at", desc=True) \
            .limit(100)
 
        if date:
            date_end = (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat()
            query = query.gte("created_at", date).lt("created_at", date_end)
 
        return query.execute().data
    except Exception as e:
        print(e)
        return []
 
 
@router.get("/summary/{merchant_id}")
async def get_merchant_summary(merchant_id: str):
    """สรุปยอดขายภาพรวม (server-side) สำหรับ Admin Dashboard"""
    try:
        txs = supabase.table("member_transactions") \
            .select("amount, status, customer_name, created_at") \
            .eq("merchant_id", merchant_id) \
            .execute().data
 
        total_revenue = sum(float(t["amount"]) for t in txs)
        total_orders  = len(txs)
        member_orders = len([t for t in txs if t.get("customer_name")])
 
        today         = datetime.now().date().isoformat()
        today_txs     = [t for t in txs if t["created_at"][:10] == today]
        today_revenue = sum(float(t["amount"]) for t in today_txs)
 
        return {
            "total_revenue": total_revenue,
            "total_orders":  total_orders,
            "member_orders": member_orders,
            "walkin_orders": total_orders - member_orders,
            "today_revenue": today_revenue,
            "today_orders":  len(today_txs)
        }
    except Exception as e:
        print(e)
        return {"total_revenue": 0, "total_orders": 0, "member_orders": 0, "walkin_orders": 0}
 
 
@router.get("/member-summary/{line_user_id}")
async def get_member_summary(line_user_id: str, merchant_id: str):
    """สรุปข้อมูลสมาชิกรายบุคคล สำหรับหน้า LIFF สะสมแต้ม"""
    try:
        txs = supabase.table("member_transactions") \
            .select("amount, created_at, receipt_id, status") \
            .eq("merchant_id", merchant_id) \
            .eq("line_user_id", line_user_id) \
            .order("created_at", desc=True) \
            .execute()
 
        total_spent    = sum(t["amount"] for t in txs.data)
        tx_count       = len(txs.data)
        first_purchase = txs.data[-1]["created_at"] if txs.data else None
 
        return {
            "total_spent":         total_spent,
            "tx_count":            tx_count,
            "first_purchase":      first_purchase,
            "recent_transactions": txs.data[:10]
        }
    except Exception:
        return {"total_spent": 0, "tx_count": 0, "first_purchase": None, "recent_transactions": []}