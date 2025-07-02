from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
import structlog

from app.core.database import get_db
from app.models.fleet import Vehicle, Route, Delivery

logger = structlog.get_logger()
router = APIRouter()

@router.get("/vehicles")
async def get_vehicles(
    status: str = None,
    vehicle_type: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get vehicles with optional filtering"""
    try:
        query = select(Vehicle)
        
        if status:
            query = query.where(Vehicle.status == status)
        if vehicle_type:
            query = query.where(Vehicle.vehicle_type == vehicle_type)
        
        result = await db.execute(query.offset(offset).limit(limit))
        vehicles = result.scalars().all()
        
        return {
            "vehicles": [
                {
                    "vehicle_id": vehicle.vehicle_id,
                    "vehicle_type": vehicle.vehicle_type,
                    "status": vehicle.status,
                    "capacity_kg": vehicle.capacity_kg,
                    "current_load_kg": vehicle.current_load_kg,
                    "average_speed_kmh": vehicle.average_speed_kmh,
                    "current_location": {
                        "id": vehicle.current_location.id,
                        "name": vehicle.current_location.name,
                        "latitude": vehicle.current_location.latitude,
                        "longitude": vehicle.current_location.longitude
                    } if vehicle.current_location else None
                } for vehicle in vehicles
            ],
            "total": len(vehicles)
        }
    except Exception as e:
        logger.error(f"Failed to get vehicles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific vehicle details"""
    try:
        result = await db.execute(select(Vehicle).where(Vehicle.vehicle_id == vehicle_id))
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        return {
            "vehicle_id": vehicle.vehicle_id,
            "vehicle_type": vehicle.vehicle_type,
            "status": vehicle.status,
            "capacity_kg": vehicle.capacity_kg,
            "current_load_kg": vehicle.current_load_kg,
            "average_speed_kmh": vehicle.average_speed_kmh,
            "current_location": {
                "id": vehicle.current_location.id,
                "name": vehicle.current_location.name,
                "latitude": vehicle.current_location.latitude,
                "longitude": vehicle.current_location.longitude
            } if vehicle.current_location else None,
            "current_route": {
                "route_id": vehicle.current_route.route_id,
                "status": vehicle.current_route.status,
                "estimated_duration_minutes": vehicle.current_route.estimated_duration_minutes
            } if vehicle.current_route else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vehicle {vehicle_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes")
async def get_routes(
    status: str = None,
    vehicle_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get routes with optional filtering"""
    try:
        query = select(Route)
        
        if status:
            query = query.where(Route.status == status)
        if vehicle_id:
            query = query.where(Route.vehicle_id == vehicle_id)
        
        result = await db.execute(query.offset(offset).limit(limit))
        routes = result.scalars().all()
        
        return {
            "routes": [
                {
                    "route_id": route.route_id,
                    "vehicle_id": route.vehicle_id,
                    "status": route.status,
                    "estimated_distance_km": route.estimated_distance_km,
                    "estimated_duration_minutes": route.estimated_duration_minutes,
                    "actual_duration_minutes": route.calculate_actual_duration(),
                    "optimization_score": route.optimization_score,
                    "delivery_count": len(route.deliveries)
                } for route in routes
            ],
            "total": len(routes)
        }
    except Exception as e:
        logger.error(f"Failed to get routes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/routes/{route_id}")
async def get_route(route_id: str, db: AsyncSession = Depends(get_db)):
    """Get specific route details"""
    try:
        result = await db.execute(select(Route).where(Route.route_id == route_id))
        route = result.scalar_one_or_none()
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "route_id": route.route_id,
            "vehicle_id": route.vehicle_id,
            "status": route.status,
            "estimated_distance_km": route.estimated_distance_km,
            "estimated_duration_minutes": route.estimated_duration_minutes,
            "actual_duration_minutes": route.calculate_actual_duration(),
            "optimization_score": route.optimization_score,
            "traffic_factor": route.traffic_factor,
            "weather_factor": route.weather_factor,
            "deliveries": [
                {
                    "delivery_id": delivery.delivery_id,
                    "status": delivery.status,
                    "weight_kg": delivery.weight_kg
                } for delivery in route.deliveries
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get route {route_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_fleet_summary(db: AsyncSession = Depends(get_db)):
    """Get fleet summary statistics"""
    try:
        result = await db.execute(select(func.count(Vehicle.vehicle_id)))
        total_vehicles = result.scalar()
        
        result = await db.execute(select(func.count(Vehicle.vehicle_id)).where(Vehicle.status == "available"))
        available_vehicles = result.scalar()
        
        result = await db.execute(select(func.count(Route.route_id)).where(Route.status.in_(["planned", "in_progress"])))
        active_routes = result.scalar()
        
        result = await db.execute(select(func.count(Delivery.delivery_id)).where(Delivery.status == "completed"))
        completed_deliveries = result.scalar()
        
        return {
            "total_vehicles": total_vehicles,
            "available_vehicles": available_vehicles,
            "utilization_rate": (total_vehicles - available_vehicles) / total_vehicles * 100 if total_vehicles > 0 else 0,
            "active_routes": active_routes,
            "completed_deliveries": completed_deliveries
        }
    except Exception as e:
        logger.error(f"Failed to get fleet summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 