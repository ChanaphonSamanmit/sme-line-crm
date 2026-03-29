from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # อ่านค่าจากไฟล์ .env อัตโนมัติ
    SUPABASE_URL: str
    SUPABASE_KEY: str
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    LIFF_URL: str = ""


    class Config:
        env_file = ".env"


settings = Settings()
