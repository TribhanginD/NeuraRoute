"""Seed data generator for the local demo database."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def _now():
    return datetime.utcnow()


def _dt(offset_minutes: int = 0) -> datetime:
    return _now() + timedelta(minutes=offset_minutes)


def seed_merchants() -> List[Dict]:
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Metro Express Logistics",
            "location": "New York, NY",
            "contact_info": "+1-555-0101",
            "created_at": _dt(-180),
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "name": "Coastal Shipping Co.",
            "location": "Los Angeles, CA",
            "contact_info": "+1-555-0102",
            "created_at": _dt(-170),
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "name": "Windy City Freight",
            "location": "Chicago, IL",
            "contact_info": "+1-555-0103",
            "created_at": _dt(-165),
        },
    ]


def seed_fleet(merchants) -> List[Dict]:
    return [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "vehicle_id": "TRUCK-001",
            "vehicle_type": "Delivery Truck",
            "capacity": 2000,
            "current_location": "New York, NY",
            "status": "available",
            "merchant_id": merchants[0]["id"],
            "geo_lat": 40.7128,
            "geo_lng": -74.0060,
            "created_at": _dt(-120),
            "updated_at": _dt(-60),
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440002",
            "vehicle_id": "TRUCK-002",
            "vehicle_type": "Cargo Van",
            "capacity": 1200,
            "current_location": "Los Angeles, CA",
            "status": "in_transit",
            "merchant_id": merchants[1]["id"],
            "geo_lat": 34.0522,
            "geo_lng": -118.2437,
            "created_at": _dt(-115),
            "updated_at": _dt(-20),
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440003",
            "vehicle_id": "REEFER-003",
            "vehicle_type": "Refrigerated Truck",
            "capacity": 1600,
            "current_location": "Chicago, IL",
            "status": "available",
            "merchant_id": merchants[2]["id"],
            "geo_lat": 41.8781,
            "geo_lng": -87.6298,
            "created_at": _dt(-110),
            "updated_at": _dt(-10),
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440004",
            "vehicle_id": "VAN-004",
            "vehicle_type": "Cargo Van",
            "capacity": 800,
            "current_location": "New York, NY",
            "status": "maintenance",
            "merchant_id": merchants[0]["id"],
            "geo_lat": 40.7306,
            "geo_lng": -73.9352,
            "created_at": _dt(-105),
            "updated_at": _dt(-5),
        },
    ]


def seed_inventory() -> List[Dict]:
    return [
        {
            "id": "770e8400-e29b-41d4-a716-446655440001",
            "item_name": "Fresh Salmon Fillets",
            "quantity": 150,
            "min_quantity": 80,
            "location": "New York Warehouse",
            "created_at": _dt(-180),
            "updated_at": _dt(-20),
        },
        {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "item_name": "Organic Spinach Crates",
            "quantity": 40,
            "min_quantity": 60,
            "location": "Los Angeles Warehouse",
            "created_at": _dt(-175),
            "updated_at": _dt(-30),
        },
        {
            "id": "770e8400-e29b-41d4-a716-446655440003",
            "item_name": "Specialty Coffee Beans",
            "quantity": 210,
            "min_quantity": 120,
            "location": "Chicago Warehouse",
            "created_at": _dt(-174),
            "updated_at": _dt(-25),
        },
        {
            "id": "770e8400-e29b-41d4-a716-446655440004",
            "item_name": "Pharmaceutical Cold-Pack",
            "quantity": 25,
            "min_quantity": 50,
            "location": "New York Warehouse",
            "created_at": _dt(-170),
            "updated_at": _dt(-15),
        },
    ]


def seed_orders(merchants) -> List[Dict]:
    return [
        {
            "id": "880e8400-e29b-41d4-a716-446655440001",
            "merchant_id": merchants[0]["id"],
            "items": "Fresh Salmon Fillets: 30",
            "status": "pending",
            "total_amount": 5400.0,
            "created_at": _dt(-55),
            "updated_at": _dt(-55),
        },
        {
            "id": "880e8400-e29b-41d4-a716-446655440002",
            "merchant_id": merchants[1]["id"],
            "items": "Organic Spinach Crates: 20, Specialty Coffee Beans: 5",
            "status": "in_transit",
            "vehicle_id": "660e8400-e29b-41d4-a716-446655440002",
            "estimated_delivery_time": _dt(120),
            "total_amount": 3200.0,
            "created_at": _dt(-50),
            "updated_at": _dt(-10),
        },
        {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "merchant_id": merchants[2]["id"],
            "items": "Specialty Coffee Beans: 15",
            "status": "delivered",
            "vehicle_id": "660e8400-e29b-41d4-a716-446655440003",
            "estimated_delivery_time": _dt(-5),
            "total_amount": 1800.0,
            "created_at": _dt(-48),
            "updated_at": _dt(-5),
        },
    ]


def seed_agents() -> List[Dict]:
    return [
        {
            "id": "aa0e8400-e29b-41d4-a716-446655440001",
            "name": "Inventory Manager AI",
            "agent_type": "inventory_management",
            "status": "active",
        },
        {
            "id": "aa0e8400-e29b-41d4-a716-446655440002",
            "name": "Route Optimizer AI",
            "agent_type": "route_optimization",
            "status": "active",
        },
        {
            "id": "aa0e8400-e29b-41d4-a716-446655440003",
            "name": "Pricing Analyst AI",
            "agent_type": "pricing_optimization",
            "status": "active",
        },
    ]


def seed_agent_actions(agents, inventory) -> List[Dict]:
    return [
        {
            "id": "bb0e8400-e29b-41d4-a716-446655440001",
            "agent_id": agents[0]["id"],
            "action_type": "reorder",
            "target_table": "purchase_orders",
            "payload": {
                "item_id": inventory[1]["id"],
                "recommended_quantity": 120,
                "reasoning": "Low leafy greens ahead of weekend demand",
                "priority": "high",
            },
            "status": "pending",
            "created_at": _dt(-20),
        },
    ]


def seed_agent_logs(agents) -> List[Dict]:
    return [
        {
            "id": "dd0e8400-e29b-41d4-a716-446655440001",
            "agent_id": agents[0]["id"],
            "agent_type": "inventory_management",
            "action": "system_started",
            "payload": {"message": "Inventory agent initialized"},
            "status": "completed",
            "timestamp": _dt(-5),
        }
    ]


def seed_purchase_orders(inventory) -> List[Dict]:
    return [
        {
            "id": "ee0e8400-e29b-41d4-a716-446655440001",
            "item_id": inventory[1]["id"],
            "item_name": inventory[1]["item_name"],
            "quantity": 120,
            "order_type": "restock",
            "requested_by": "inventory_agent",
            "status": "pending",
            "location": inventory[1]["location"],
            "reason": "Replenish leafy greens for weekend spike",
            "created_at": _dt(-15),
            "expected_delivery": _dt(48),
        },
    ]


def seed_disposal_orders(inventory) -> List[Dict]:
    return [
        {
            "id": "ff0e8400-e29b-41d4-a716-446655440001",
            "item_id": inventory[0]["id"],
            "quantity": 10,
            "disposal_type": "donation",
            "status": "pending",
            "reason": "Near expiry stock donation",
            "created_at": _dt(-10),
        },
    ]


def seed_routes(fleet) -> List[Dict]:
    return [
        {
            "id": "990e8400-e29b-41d4-a716-446655440001",
            "vehicle_id": fleet[0]["id"],
            "status": "active",
            "route_points": {
                "points": [
                    {"lat": 40.7128, "lng": -74.0060, "address": "NY Warehouse"},
                    {"lat": 40.7589, "lng": -73.9851, "address": "Times Square"},
                    {"lat": 40.7505, "lng": -73.9934, "address": "Penn Station"},
                ]
            },
            "created_at": _dt(-30),
        },
        {
            "id": "990e8400-e29b-41d4-a716-446655440002",
            "vehicle_id": fleet[1]["id"],
            "status": "active",
            "route_points": {
                "points": [
                    {"lat": 34.0522, "lng": -118.2437, "address": "LA Warehouse"},
                    {"lat": 34.1016, "lng": -118.3267, "address": "Hollywood"},
                    {"lat": 34.0736, "lng": -118.2400, "address": "Downtown LA"},
                ]
            },
            "created_at": _dt(-25),
        },
    ]


def build_seed_data():
    merchants = seed_merchants()
    fleet = seed_fleet(merchants)
    inventory = seed_inventory()
    orders = seed_orders(merchants)
    agents = seed_agents()
    agent_actions = seed_agent_actions(agents, inventory)
    agent_logs = seed_agent_logs(agents)
    purchase_orders = seed_purchase_orders(inventory)
    disposal_orders = seed_disposal_orders(inventory)
    routes = seed_routes(fleet)
    return {
        "merchants": merchants,
        "fleet": fleet,
        "inventory": inventory,
        "orders": orders,
        "agents": agents,
        "agent_actions": agent_actions,
        "agent_logs": agent_logs,
        "purchase_orders": purchase_orders,
        "disposal_orders": disposal_orders,
        "routes": routes,
    }
