import requests
import json
import os
from dotenv import load_dotenv

# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================
# This command automatically finds your .env file and loads the secrets
load_dotenv()

# Securely pull the token from the .env file
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# Safety Check: Stop the script if the token is missing
if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ ERROR: Could not find LINE_CHANNEL_ACCESS_TOKEN in the .env file! Make sure your .env file is in the same folder.")

# ==========================================
# 2. CONFIGURATION 
# ==========================================
# Replace this with your actual LIFF URL
LIFF_URL = os.getenv("LIFE_URL") 

# Make sure you have an image named exactly this in the same folder
IMAGE_PATH = "richmenu_image.jpg" 

HEADERS = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ==========================================
# 3. DEFINE THE MENU LAYOUT (3 Buttons)
# ==========================================
rich_menu_data = {
    "size": {
        "width": 2500,
        "height": 1686
    },
    "selected": True,
    "name": "SME POS Menu",
    "chatBarText": "เมนู (Menu)",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": 2500, "height": 843},
            "action": {"type": "uri", "uri": LIFF_URL}
        },
        {
            "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
            "action": {"type": "message", "text": "เช็คแต้ม"}
        },
        {
            "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
            "action": {"type": "message", "text": "โปรโมชั่น"}
        }
    ]
}

def create_rich_menu():
    """Step 1: Send the layout to LINE and get a Menu ID"""
    print("⏳ Creating Rich Menu layout...")
    response = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=HEADERS,
        data=json.dumps(rich_menu_data)
    )
    response.raise_for_status() # Throws an error if LINE rejects the request
    rich_menu_id = response.json().get("richMenuId")
    print(f"✅ Created! Rich Menu ID: {rich_menu_id}")
    return rich_menu_id

def upload_image(rich_menu_id):
    """Step 2: Upload the actual JPG/PNG image to the Menu ID"""
    print("⏳ Uploading image...")
    image_headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "image/jpeg"
    }
    with open(IMAGE_PATH, "rb") as f:
        response = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers=image_headers,
            data=f
        )
        response.raise_for_status()
    print("✅ Image uploaded successfully!")

def set_default_menu(rich_menu_id):
    """Step 3: Tell LINE to show this menu to all customers"""
    print("⏳ Setting as default menu for all users...")
    response = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=HEADERS
    )
    response.raise_for_status()
    print("✅ Successfully set as default! Check your LINE app.")

# ==========================================
# 4. EXECUTE THE SCRIPT
# ==========================================
if __name__ == "__main__":
    try:
        menu_id = create_rich_menu()
        upload_image(menu_id)
        set_default_menu(menu_id)
        print("\n🎉 ALL DONE! Your professional Rich Menu is live.")
    except Exception as e:
        print(f"\n❌ Error: {e}")