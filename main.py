import os
import pathlib

# Set CWD to project root (important for Vercel serverless)
root = pathlib.Path(__file__).parent.resolve()
os.chdir(root)

# Vercel bundles Python files but not static assets via @vercel/python includeFiles.
# Create empty stub directories so FastAPI's StaticFiles mount doesn't crash on startup.
# Static files are served by Vercel CDN routes (see vercel.json).
for subdir in ["static/admin", "static/liff"]:
    (root / subdir).mkdir(parents=True, exist_ok=True)

from app.main import app
