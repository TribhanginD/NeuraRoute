from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import logging

from app.core.database import get_db
from app.models.inventory import InventoryItem, SKU, Location

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/items")
async def get_inventory_items(
    location_id: int = None,
    sku_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get inventory items with optional filtering"""
    try:
        query = select(InventoryItem)
        
        if location_id:
            query = query.where(InventoryItem.location_id == location_id)
        
        if sku_id:
            query = query.where(InventoryItem.sku_id == sku_id)
        
        result = await db.execute(query.offset(offset).limit(limit))
        items = result.scalars().all()
        
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
                        "sku_id": item.sku.id,
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
async def get_inventory_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific inventory item"""
    try:
        result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
        item = result.scalar_one_or_none()
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
                "sku_id": item.sku.id,
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
    db: AsyncSession = Depends(get_db)
):
    """Get SKUs with optional filtering"""
    try:
        query = select(SKU)
        
        if category:
            query = query.where(SKU.category == category)
        
        result = await db.execute(query.offset(offset).limit(limit))
        skus = result.scalars().all()
        
        return {
            "skus": [
                {
                    "sku_id": sku.id,
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
async def get_sku(sku_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific SKU details"""
    try:
        result = await db.execute(select(SKU).where(SKU.id == sku_id))
        sku = result.scalar_one_or_none()
        if not sku:
            raise HTTPException(status_code=404, detail="SKU not found")
        
        return {
            "sku_id": sku.id,
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
    db: AsyncSession = Depends(get_db)
):
    """Get all locations"""
    try:
        result = await db.execute(select(Location).offset(offset).limit(limit))
        locations = result.scalars().all()
        
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
async def get_location(location_id: int, db: AsyncSession = Depends(get_db)):
    """Get specific location details"""
    try:
        result = await db.execute(select(Location).where(Location.id == location_id))
        location = result.scalar_one_or_none()
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
async def get_inventory_summary(db: AsyncSession = Depends(get_db)):
    """Get inventory summary statistics"""
    try:
        # Get total counts
        result = await db.execute(select(func.count(InventoryItem.id)))
        total_items = result.scalar()
        
        result = await db.execute(select(func.count(SKU.id)))
        total_skus = result.scalar()
        
        result = await db.execute(select(func.count(Location.id)))
        total_locations = result.scalar()
        
        # Get low stock items (less than 10 available)
        result = await db.execute(
            select(func.count(InventoryItem.id)).where(InventoryItem.available_quantity < 10)
        )
        low_stock_items = result.scalar()
        
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