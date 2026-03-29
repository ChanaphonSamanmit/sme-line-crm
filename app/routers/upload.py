  app/routers/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import supabase
import uuid


router = APIRouter()


ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # ตรวจสอบประเภทไฟล์
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"ประเภทไฟล์ไม่รองรับ: {content_type} (รองรับเฉพาะ JPG, PNG, GIF, WEBP)")


    try:
        file_content = await file.read()


        # ตรวจสอบขนาดไฟล์
        if len(file_content) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="ไฟล์ใหญ่เกิน 5MB")


        # ตั้งชื่อไฟล์ใหม่
        ext_map = {"image/jpeg": "jpg", "image/jpg": "jpg", "image/png": "png", "image/gif": "gif", "image/webp": "webp"}
        file_ext = ext_map.get(content_type, "jpg")
        new_filename = f"{uuid.uuid4()}.{file_ext}"  # ไม่ใส่ subfolder


        # อัปโหลดขึ้น Supabase Storage
        bucket_name = "products"
        supabase.storage.from_(bucket_name).upload(
            path=new_filename,
            file=file_content,
            file_options={"content-type": content_type}
        )


        # ขอ Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(new_filename)


        return {"status": "ok", "url": public_url}


    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Upload Error: {e}") # เพิ่มบรรทัดนี้ มันจะปริ้นท์บอกในหน้าจอสีดำเลยว่าพังเพราะอะไร
        raise HTTPException(status_code=500, detail=str(e))
