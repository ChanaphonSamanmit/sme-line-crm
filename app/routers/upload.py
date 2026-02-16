from fastapi import APIRouter, UploadFile, File, HTTPException
from app.database import supabase
import uuid

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1. อ่านไฟล์และตั้งชื่อใหม่กันซ้ำ
        file_content = await file.read()
        file_ext = file.filename.split(".")[-1]
        new_filename = f"{uuid.uuid4()}.{file_ext}"

        # 2. อัปโหลดขึ้น Supabase Storage (Bucket ชื่อ 'products')
        bucket_name = "products"
        res = supabase.storage.from_(bucket_name).upload(
            path=new_filename,
            file=file_content,
            file_options={"content-type": file.content_type}
        )

        # 3. ขอ Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(new_filename)
        
        return {"status": "ok", "url": public_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))