from pydantic import BaseModel
from typing import Optional

# ==================== VENDOR SCHEMAS ====================

class VendorBase(BaseModel):
    name: str
    phone: str

class CreateVendor(VendorBase):
    """Schema for creating a new vendor (request model)"""
    pass

class ShowVendor(VendorBase):
    """Schema for displaying vendor info (response model)"""
    id: int

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models


# ==================== PURCHASE ORDER SCHEMAS ====================

class OrderBase(BaseModel):
    vendor_id: int
    item_name: str
    quantity: int

class CreateOrder(OrderBase):
    """Schema for creating a new purchase order (request model)"""
    pass

class ShowOrder(OrderBase):
    """Schema for displaying purchase order info (response model)"""
    id: int
    status: str = "Pending"
    vendor: Optional[ShowVendor] = None  # Shows vendor details

    class Config:
        from_attributes = True


# ==================== INVENTORY SCHEMAS ====================

class ShowInventory(BaseModel):
    """Schema for displaying inventory info (response model)"""
    id: int
    item_name: str
    quantity: int

    class Config:
        from_attributes = True