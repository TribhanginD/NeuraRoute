from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .session import Base


def default_uuid() -> str:
    return str(uuid.uuid4())


class DictionaryMixin:
    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for column in self.__table__.columns:
            result[column.name] = getattr(self, column.name)
        return result


class Merchant(Base, DictionaryMixin):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=default_uuid)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    contact_info = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    fleet = relationship("Fleet", back_populates="merchant")


class Fleet(Base, DictionaryMixin):
    __tablename__ = "fleet"

    id = Column(String, primary_key=True, default=default_uuid)
    vehicle_id = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    capacity = Column(Integer, default=0)
    current_location = Column(String, nullable=True)
    status = Column(String, default="available")
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    geo_lat = Column(Float, nullable=True)
    geo_lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="fleet")


class Inventory(Base, DictionaryMixin):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True, default=default_uuid)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=0)
    location = Column(String, nullable=True)
    min_quantity = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Order(Base, DictionaryMixin):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=default_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=True)
    items = Column(Text, nullable=False)
    status = Column(String, default="pending")
    total_amount = Column(Float, default=0.0)
    vehicle_id = Column(String, nullable=True)
    estimated_pickup_time = Column(String, nullable=True)
    estimated_delivery_time = Column(String, nullable=True)
    route = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Route(Base, DictionaryMixin):
    __tablename__ = "routes"

    id = Column(String, primary_key=True, default=default_uuid)
    vehicle_id = Column(String, nullable=False)
    status = Column(String, default="active")
    route_points = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Agent(Base, DictionaryMixin):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=default_uuid)
    name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentAction(Base, DictionaryMixin):
    __tablename__ = "agent_actions"

    id = Column(String, primary_key=True, default=default_uuid)
    agent_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    target_table = Column(String, nullable=True)
    item_id = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    priority = Column(String, default="medium")
    reasoning = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    route_data = Column(JSON, nullable=True)
    new_price = Column(Float, nullable=True)
    strategy = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)


class AgentLog(Base, DictionaryMixin):
    __tablename__ = "agent_logs"

    id = Column(String, primary_key=True, default=default_uuid)
    agent_id = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)
    action = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)
    details = Column(JSON, nullable=True)
    status = Column(String, default="completed")
    timestamp = Column(DateTime, default=datetime.utcnow)


class AgentDecision(Base, DictionaryMixin):
    __tablename__ = "agent_decisions"

    id = Column(String, primary_key=True, default=default_uuid)
    decision_type = Column(String, nullable=False)
    agent_id = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    decision = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)


class SimulationStatus(Base, DictionaryMixin):
    __tablename__ = "simulation_status"

    id = Column(String, primary_key=True, default=default_uuid)
    is_running = Column(Boolean, default=False)
    current_tick = Column(Integer, default=0)
    total_ticks = Column(Integer, default=96)
    tick_interval_seconds = Column(Integer, default=900)
    current_time = Column(String, nullable=True)
    last_tick_time = Column(String, nullable=True)
    started_at = Column(String, nullable=True)
    estimated_completion = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class PurchaseOrder(Base, DictionaryMixin):
    __tablename__ = "purchase_orders"

    id = Column(String, primary_key=True, default=default_uuid)
    item_id = Column(String, nullable=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    requested_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(String, nullable=True)
    actual_delivery = Column(String, nullable=True)
    location = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    supplier_info = Column(JSON, nullable=True)
    cost_per_unit = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)


class DisposalOrder(Base, DictionaryMixin):
    __tablename__ = "disposal_orders"

    id = Column(String, primary_key=True, default=default_uuid)
    item_id = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    disposal_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    disposal_method = Column(String, nullable=True)
    cost_savings = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
