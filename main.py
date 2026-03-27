from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Vendor, PurchaseOrder, Inventory
from schemas import CreateVendor, ShowVendor, CreateOrder, ShowOrder, ShowInventory

# Create all database tables
Base.metadata.create_all(bind=engine, checkfirst=True)

# Initialize FastAPI app
app = FastAPI(
    title="Mini ERP",
    description="A simple Enterprise Resource Planning system",
    version="1.0.0"
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Mini ERP API",
        "status": "running",
        "version": "1.0.0"
    }


# ==================== VENDOR ENDPOINTS ====================

@app.post("/vendors", response_model=ShowVendor)
def create_vendor(vendor: CreateVendor, db: Session = Depends(get_db)):
    """
    Create a new vendor
    
    - **name**: Vendor name
    - **phone**: Vendor phone number
    """
    # Create new vendor object
    new_vendor = Vendor(name=vendor.name, phone=vendor.phone)
    
    # Add to database
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    
    return new_vendor


@app.get("/vendors", response_model=list[ShowVendor])
def get_vendors(db: Session = Depends(get_db)):
    """Get all vendors"""
    vendors = db.query(Vendor).all()
    return vendors


# ==================== PURCHASE ORDER ENDPOINTS ====================

@app.post("/orders", response_model=ShowOrder)
def create_order(order: CreateOrder, db: Session = Depends(get_db)):
    """
    Create a new purchase order
    
    - **vendor_id**: ID of the vendor
    - **item_name**: Name of the item to purchase
    - **quantity**: Quantity of items to purchase
    - **status**: Order status (default: "Pending")
    """
    # Verify vendor exists
    vendor = db.query(Vendor).filter(Vendor.id == order.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Create new purchase order
    new_order = PurchaseOrder(
        vendor_id=order.vendor_id,
        item_name=order.item_name,
        quantity=order.quantity,
        status="Pending"  # Set default status
    )
    
    # Add to database
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order


@app.get("/orders", response_model=list[ShowOrder])
def get_orders(db: Session = Depends(get_db)):
    """Get all purchase orders"""
    orders = db.query(PurchaseOrder).all()
    return orders


# ==================== GOODS RECEIPT ENDPOINT ====================

@app.post("/orders/{order_id}/receive", response_model=ShowOrder)
def receive_goods(order_id: int, db: Session = Depends(get_db)):
    """
    Receive goods for a purchase order
    
    - Updates order status to "Received"
    - Updates inventory (adds quantity if item exists, creates new item if not)
    """
    # Find the order
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    # Check if order is already received
    if order.status == "Received":
        raise HTTPException(status_code=400, detail="Order already received")
    
    # Update order status
    order.status = "Received"
    
    # Update inventory
    inventory_item = db.query(Inventory).filter(Inventory.item_name == order.item_name).first()
    
    if inventory_item:
        # Item exists - add quantity
        inventory_item.quantity += order.quantity
    else:
        # Item doesn't exist - create new inventory item
        new_inventory_item = Inventory(
            item_name=order.item_name,
            quantity=order.quantity
        )
        db.add(new_inventory_item)
    
    # Commit all changes
    db.commit()
    db.refresh(order)
    
    return order


# ==================== INVENTORY ENDPOINT ====================

@app.get("/inventory", response_model=list[ShowInventory])
def get_inventory(db: Session = Depends(get_db)):
    """Get all inventory items"""
    inventory_items = db.query(Inventory).all()
    return inventory_items