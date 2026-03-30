from fastapi import APIRouter, Request, Header
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from app.config import settings
from app.database import supabase

router = APIRouter()

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

@router.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    body_str = body.decode("utf-8")
    if not x_line_signature: return "OK"
    try:
        handler.handle(body_str, x_line_signature)
    except InvalidSignatureError:
        return "OK"
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    user_id = event.source.user_id
    reply_msg = ""

    # 1. เช็คแต้ม (ง่ายๆ ดึงจาก Transaction รวมกัน)
    if "เช็คแต้ม" in text or "คะแนน" in text:
        try:
            # ดึงข้อมูลประวัติการสะสมแต้ม
            txs = supabase.table("member_transactions").select("amount").eq("line_user_id", user_id).execute()
            total_spent = sum(float(t['amount']) for t in txs.data)
            points = int(total_spent / 100)
            reply_msg = f"💰 ยอดซื้อสะสม: {total_spent:,.2f} บาท\n⭐ คะแนนของคุณ: {points} แต้ม"
        except:
            reply_msg = "ไม่สามารถดึงข้อมูลแต้มได้ในขณะนี้"

    # 2. กรณีอื่นๆ
    else:
        reply_msg = "สวัสดีครับ! 👋\nคุณสามารถกดเมนูด้านล่างเพื่อสะสมแต้ม หรือพิมพ์คำว่า 'เช็คแต้ม' เพื่อดูคะแนนสะสมได้เลยครับ"

    # ส่งข้อความกลับ พร้อมปุ่มทางลัด (Quick Reply)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=reply_msg,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="เช็คแต้ม", text="เช็คแต้ม")),
                QuickReplyButton(action=MessageAction(label="เวลาทำการ", text="เวลาทำการ"))
            ])
        )
    )