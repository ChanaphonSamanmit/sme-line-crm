from pydantic import BaseModel
from typing import Optional, List
 
 
# ── Product Models ──
 
class ProductCreate(BaseModel):
    merchant_id: str
    name: str
    price: float
    cost_price: float = 0
    image_url: Optional[str] = ""
 
 
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    image_url: Optional[str] = None
 
 
# ── Cart & QR Models ──
 
class CartItem(BaseModel):
    product_id: str
    name: str
    price: float
    cost: float
    quantity: int
 
 
class GenerateQRRequest(BaseModel):
    merchant_id: str
    items: List[CartItem]
    total_amount: float
    discount: float = 0
 
 
class ClaimPointRequest(BaseModel):
    line_user_id: str
    qr_id: str
    display_name: str
    picture_url: str
