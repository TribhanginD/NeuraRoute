from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import structlog

from app.core.database import get_db
from app.models.merchant import Merchant, Order, Customer

logger = structlog.get_logger()
router = APIRouter()

@router.get("/")
async def get_merchants(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all merchants"""
    try:
        merchants = db.query(Merchant).offset(offset).limit(limit).all()
        
        return {
            "merchants": [
                {
                    "merchant_id": merchant.merchant_id,
                    "name": merchant.name,
                    "business_type": merchant.business_type,
                    "status": merchant.status,
                    "location": {
                        "id": merchant.location.id,
                        "name": merchant.location.name,
                        "address": merchant.location.address,
                        "latitude": merchant.location.latitude,
                        "longitude": merchant.location.longitude
                    } if merchant.location else None
                } for merchant in merchants
            ],
            "total": len(merchants)
        }
    except Exception as e:
        logger.error("Failed to get merchants", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    """Get specific merchant details"""
    try:
        merchant = db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first()
        if not merchant:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        return {
            "merchant_id": merchant.merchant_id,
            "name": merchant.name,
            "business_type": merchant.business_type,
            "status": merchant.status,
            "contact_email": merchant.contact_email,
            "contact_phone": merchant.contact_phone,
            "location": {
                "id": merchant.location.id,
                "name": merchant.location.name,
                "address": merchant.location.address,
                "latitude": merchant.location.latitude,
                "longitude": merchant.location.longitude
            } if merchant.location else None,
            "created_at": merchant.created_at.isoformat(),
            "updated_at": merchant.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get merchant {merchant_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{merchant_id}/orders")
async def get_merchant_orders(
    merchant_id: str,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get orders for a specific merchant"""
    try:
        query = db.query(Order).filter(Order.merchant_id == merchant_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.offset(offset).limit(limit).all()
        
        return {
            "orders": [
                {
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "items_count": len(order.order_items),
                    "created_at": order.created_at.isoformat(),
                    "customer": {
                        "customer_id": order.customer.customer_id,
                        "name": order.customer.name,
                        "email": order.customer.email
                    } if order.customer else None
                } for order in orders
            ],
            "total": len(orders)
        }
    except Exception as e:
        logger.error(f"Failed to get orders for merchant {merchant_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders(
    status: str = None,
    merchant_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all orders with optional filtering"""
    try:
        query = db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        if merchant_id:
            query = query.filter(Order.merchant_id == merchant_id)
        
        orders = query.offset(offset).limit(limit).all()
        
        return {
            "orders": [
                {
                    "order_id": order.order_id,
                    "merchant_id": order.merchant_id,
                    "customer_id": order.customer_id,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "items_count": len(order.order_items),
                    "created_at": order.created_at.isoformat(),
                    "merchant": {
                        "merchant_id": order.merchant.merchant_id,
                        "name": order.merchant.name
                    } if order.merchant else None,
                    "customer": {
                        "customer_id": order.customer.customer_id,
                        "name": order.customer.name
                    } if order.customer else None
                } for order in orders
            ],
            "total": len(orders)
        }
    except Exception as e:
        logger.error("Failed to get orders", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}")
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get specific order details"""
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "order_id": order.order_id,
            "merchant_id": order.merchant_id,
            "customer_id": order.customer_id,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "merchant": {
                "merchant_id": order.merchant.merchant_id,
                "name": order.merchant.name,
                "business_type": order.merchant.business_type
            } if order.merchant else None,
            "customer": {
                "customer_id": order.customer.customer_id,
                "name": order.customer.name,
                "email": order.customer.email,
                "phone": order.customer.phone
            } if order.customer else None,
            "items": [
                {
                    "sku_id": item.sku_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "sku": {
                        "sku_id": item.sku.sku_id,
                        "name": item.sku.name,
                        "category": item.sku.category
                    } if item.sku else None
                } for item in order.order_items
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get order {order_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers")
async def get_customers(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all customers"""
    try:
        customers = db.query(Customer).offset(offset).limit(limit).all()
        
        return {
            "customers": [
                {
                    "customer_id": customer.customer_id,
                    "name": customer.name,
                    "email": customer.email,
                    "phone": customer.phone,
                    "customer_rating": customer.customer_rating,
                    "total_orders": len(customer.orders)
                } for customer in customers
            ],
            "total": len(customers)
        }
    except Exception as e:
        logger.error("Failed to get customers", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_merchants_summary(db: Session = Depends(get_db)):
    """Get merchants summary statistics"""
    try:
        total_merchants = db.query(Merchant).count()
        active_merchants = db.query(Merchant).filter(Merchant.status == "active").count()
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status == "pending").count()
        total_customers = db.query(Customer).count()
        
        return {
            "total_merchants": total_merchants,
            "active_merchants": active_merchants,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_customers": total_customers,
            "order_completion_rate": ((total_orders - pending_orders) / total_orders * 100) if total_orders > 0 else 0
        }
    except Exception as e:
        logger.error("Failed to get merchants summary", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 