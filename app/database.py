from supabase import create_client, Client
from app.config import settings


# สร้างการเชื่อมต่อกับ Supabase โดยใช้ URL และ KEY จากไฟล์ .env
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
