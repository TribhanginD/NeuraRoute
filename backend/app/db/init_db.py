"""Utility to initialize the local SQL database with seed data."""

from __future__ import annotations

from sqlalchemy.orm import Session

from . import models
from .sample_data import build_seed_data
from .session import Base, engine, SessionLocal


def seed_table(session: Session, model, rows):
    if not rows:
        return
    if session.query(model).count() > 0:
        return
    session.bulk_insert_mappings(model, rows)
    session.commit()


def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seeds = build_seed_data()
        seed_table(session, models.Merchant, seeds["merchants"])
        seed_table(session, models.Fleet, seeds["fleet"])
        seed_table(session, models.Inventory, seeds["inventory"])
        seed_table(session, models.Order, seeds["orders"])
        seed_table(session, models.Route, seeds["routes"])
        seed_table(session, models.Agent, seeds["agents"])
        seed_table(session, models.AgentAction, seeds["agent_actions"])
        seed_table(session, models.AgentLog, seeds["agent_logs"])
        seed_table(session, models.PurchaseOrder, seeds["purchase_orders"])
        seed_table(session, models.DisposalOrder, seeds["disposal_orders"])
