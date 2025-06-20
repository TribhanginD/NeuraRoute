from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import structlog

from app.core.database import get_db
from app.models.inventory import InventoryItem, SKU, Location

logger = structlog.get_logger()
router = APIRouter()

@router.get("/items")
async def get_inventory_items(
    location_id: int = None,
    sku_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get inventory items with optional filtering"""
    try:
        query = db.query(InventoryItem)
        
        if location_id:
            query = query.filter(InventoryItem.location_id == location_id)
        if sku_id:
            query = query.filter(InventoryItem.sku_id == sku_id)
        
        items = query.offset(offset).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": item.id,
                    "sku_id": item.sku_id,
                    "location_id": item.location_id,
                    "quantity": item.quantity,
                    "reserved_quantity": item.reserved_quantity,
                    "available_quantity": item.available_quantity,
                    "last_updated": item.last_updated.isoformat(),
                    "sku": {
                        "sku_id": item.sku.sku_id,
                        "name": item.sku.name,
                        "category": item.sku.category,
                        "unit": item.sku.unit
                    } if item.sku else None,
                    "location": {
                        "id": item.location.id,
                        "name": item.location.name,
                        "address": item.location.address
                    } if item.location else None
                } for item in items
            ],
            "total": len(items)
        }
    except Exception as e:
        logger.error("Failed to get inventory items", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}")
async def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Get specific inventory item"""
    try:
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        return {
            "id": item.id,
            "sku_id": item.sku_id,
            "location_id": item.location_id,
            "quantity": item.quantity,
            "reserved_quantity": item.reserved_quantity,
            "available_quantity": item.available_quantity,
            "last_updated": item.last_updated.isoformat(),
            "sku": {
                "sku_id": item.sku.sku_id,
                "name": item.sku.name,
                "category": item.sku.category,
                "unit": item.sku.unit,
                "description": item.sku.description
            } if item.sku else None,
            "location": {
                "id": item.location.id,
                "name": item.location.name,
                "address": item.location.address,
                "latitude": item.location.latitude,
                "longitude": item.location.longitude
            } if item.location else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get inventory item {item_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skus")
async def get_skus(
    category: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get SKUs with optional filtering"""
    try:
        query = db.query(SKU)
        
        if category:
            query = query.filter(SKU.category == category)
        
        skus = query.offset(offset).limit(limit).all()
        
        return {
            "skus": [
                {
                    "sku_id": sku.sku_id,
                    "name": sku.name,
                    "category": sku.category,
                    "unit": sku.unit,
                    "description": sku.description,
                    "created_at": sku.created_at.isoformat()
                } for sku in skus
            ],
            "total": len(skus)
        }
    except Exception as e:
        logger.error("Failed to get SKUs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skus/{sku_id}")
async def get_sku(sku_id: str, db: Session = Depends(get_db)):
    """Get specific SKU details"""
    try:
        sku = db.query(SKU).filter(SKU.sku_id == sku_id).first()
        if not sku:
            raise HTTPException(status_code=404, detail="SKU not found")
        
        return {
            "sku_id": sku.sku_id,
            "name": sku.name,
            "category": sku.category,
            "unit": sku.unit,
            "description": sku.description,
            "created_at": sku.created_at.isoformat(),
            "updated_at": sku.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get SKU {sku_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations")
async def get_locations(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all locations"""
    try:
        locations = db.query(Location).offset(offset).limit(limit).all()
        
        return {
            "locations": [
                {
                    "id": location.id,
                    "name": location.name,
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "location_type": location.location_type
                } for location in locations
            ],
            "total": len(locations)
        }
    except Exception as e:
        logger.error("Failed to get locations", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations/{location_id}")
async def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get specific location details"""
    try:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {
            "id": location.id,
            "name": location.name,
            "address": location.address,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "location_type": location.location_type,
            "created_at": location.created_at.isoformat(),
            "updated_at": location.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get location {location_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_inventory_summary(db: Session = Depends(get_db)):
    """Get inventory summary statistics"""
    try:
        total_items = db.query(InventoryItem).count()
        total_skus = db.query(SKU).count()
        total_locations = db.query(Location).count()
        
        # Get low stock items (less than 10 available)
        low_stock_items = db.query(InventoryItem).filter(
            InventoryItem.available_quantity < 10
        ).count()
        
        return {
            "total_items": total_items,
            "total_skus": total_skus,
            "total_locations": total_locations,
            "low_stock_items": low_stock_items,
            "low_stock_percentage": (low_stock_items / total_items * 100) if total_items > 0 else 0
        }
    except Exception as e:
        logger.error("Failed to get inventory summary", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 