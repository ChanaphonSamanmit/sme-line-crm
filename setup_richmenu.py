import json
import logging
import os
import sys
import requests
from dotenv import load_dotenv

# ==========================================
# 1. CONFIGURATION & LOGGING
# ==========================================
# Configure standard logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
if not CHANNEL_ACCESS_TOKEN:
    logger.error("Could not find LINE_CHANNEL_ACCESS_TOKEN in the .env file.")
    sys.exit(1)

LIFF_URL = os.getenv("LIFF_URL", "https://liff.line.me/YOUR_LIFF_ID")
IMAGE_PATH = "richmenu_image.jpg"

HEADERS = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ==========================================
# 2. MENU LAYOUT DEFINITION
# ==========================================
RICH_MENU_DATA = {
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
            "action": {"type": "message", "text": "เวลาทำการ"}
        }
    ]
}

# ==========================================
# 3. CORE FUNCTIONS
# ==========================================
def create_rich_menu() -> str:
    """
    Transmits the Rich Menu layout to the LINE API to instantiate a new menu.

    Returns:
        str: The generated Rich Menu ID provided by the LINE platform.
    """
    logger.info("Creating Rich Menu layout...")
    response = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers=HEADERS,
        data=json.dumps(RICH_MENU_DATA)
    )
    response.raise_for_status()
    
    rich_menu_id = response.json().get("richMenuId")
    logger.info("Rich Menu layout created. ID: %s", rich_menu_id)
    return rich_menu_id

def upload_image(rich_menu_id: str) -> None:
    """
    Uploads the local static image asset to the designated Rich Menu ID.

    Args:
        rich_menu_id (str): The target Rich Menu ID to attach the image to.
    """
    logger.info("Uploading image asset to Rich Menu ID: %s", rich_menu_id)
    image_headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "image/jpeg"
    }
    with open(IMAGE_PATH, "rb") as image_file:
        response = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers=image_headers,
            data=image_file
        )
        response.raise_for_status()
        
    logger.info("Image asset uploaded successfully.")

def set_default_menu(rich_menu_id: str) -> None:
    """
    Configures the specified Rich Menu as the global default for all LINE Official Account users.

    Args:
        rich_menu_id (str): The ID of the Rich Menu to set as default.
    """
    logger.info("Setting Rich Menu ID %s as the global default...", rich_menu_id)
    response = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=HEADERS
    )
    response.raise_for_status()
    logger.info("Global default menu set successfully.")

# ==========================================
# 4. SCRIPT EXECUTION
# ==========================================
if __name__ == "__main__":
    try:
        logger.info("Initializing Rich Menu deployment sequence.")
        menu_id = create_rich_menu()
        upload_image(menu_id)
        set_default_menu(menu_id)
        logger.info("Deployment sequence completed successfully.")
        
    except Exception as e:
        logger.error("Deployment failed due to an exception: %s", e)
        sys.exit(1)