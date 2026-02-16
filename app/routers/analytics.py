from fastapi import APIRouter, HTTPException
from app.database import supabase
from datetime import datetime, date, timedelta

router = APIRouter()

@router.get("/dashboard-kpi/{merchant_id}")
async def get_dashboard_kpi(merchant_id: str):
    today = date.today().isoformat()
    
    # 1. ดึง Transaction ทั้งหมดของวันนี้ (ทั้ง Member และ Non-Member)
    # เพราะตอนนี้เราบันทึกทุกยอดขายลงตารางนี้แล้ว
    all_txs = supabase.table("member_transactions") \
        .select("amount, line_user_id") \
        .eq("merchant_id", merchant_id) \
        .gte("created_at", today) \
        .execute()
    
    total_rev = 0
    member_rev = 0
    
    # วนลูปคำนวณแยกประเภท
    for tx in all_txs.data:
        amount = tx['amount']
        total_rev += amount # บวกยอดรวมเสมอ
        
        if tx['line_user_id']: # ถ้ามี User ID แปลว่าเป็นสมาชิก
            member_rev += amount

    # คำนวณส่วนต่าง (ขาจร)
    non_member_rev = total_rev - member_rev

    # คำนวณ %
    member_pct = int((member_rev / total_rev * 100)) if total_rev > 0 else 0

    # Action Recommendation
    action_needed = "✅ ระบบกำลังบันทึกยอดขาย Real-time"
    if total_rev == 0:
        action_needed = "🛒 รอการขายแรกของวัน..."
    elif member_pct < 20:
        action_needed = "📢 ชวนลูกค้าสแกนรับแต้มเพิ่มขึ้น"

    return {
        "question_1_today_sales": total_rev,          # ยอดขายจริงจากระบบ POS
        "question_2_member_contribution": member_rev,     # ยอดจากสมาชิกที่สแกน
        "question_3_trend": "Real-time Tracking",           
        "question_4_action": action_needed,               
        "details": {
            "non_member": non_member_rev,
            "member_pct": member_pct
        }
    }

# API กรอกยอดรายวัน (เก็บไว้เผื่อแก้ แต่หลักๆ ไม่ต้องใช้แล้ว)
@router.post("/daily-input")
async def save_daily_input(data: dict):
    return {"status": "ok", "message": "ระบบเปลี่ยนเป็น Real-time แล้ว ไม่จำเป็นต้องบันทึกยอดเอง"}

@router.get("/transactions/{merchant_id}")
async def get_transaction_history(merchant_id: str):
    # ดึง 50 รายการล่าสุด พร้อมข้อมูลสินค้าที่ซื้อ
    try:
        res = supabase.table("member_transactions")\
            .select("*, transaction_items(product_id, quantity, price_at_sale, products(name))")\
            .eq("merchant_id", merchant_id)\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        return res.data
    except Exception as e:
        print(e)
        return []