from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy import asc, desc as desc_func
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import SessionLocal


TABLE_MODEL_MAP: Dict[str, Type[models.DictionaryMixin]] = {
    "merchants": models.Merchant,
    "fleet": models.Fleet,
    "inventory": models.Inventory,
    "orders": models.Order,
    "routes": models.Route,
    "agents": models.Agent,
    "agent_actions": models.AgentAction,
    "agent_logs": models.AgentLog,
    "agent_decisions": models.AgentDecision,
    "simulation_status": models.SimulationStatus,
    "purchase_orders": models.PurchaseOrder,
    "disposal_orders": models.DisposalOrder,
}


class QueryResult:
    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, count: Optional[int] = None):
        self.data = data or []
        self.count = count


class LocalSupabaseQuery:
    def __init__(self, model: Type[models.DictionaryMixin]):
        self.model = model
        self.session: Session = SessionLocal()
        self._filters: List[tuple[str, str, Any]] = []
        self._order_by: Optional[tuple[str, bool]] = None
        self._limit: Optional[int] = None
        self._count_mode: Optional[str] = None
        self._operation: str = "select"
        self._payload: Any = None

    # Filter helpers
    def eq(self, column: str, value: Any):
        self._filters.append((column, "eq", value))
        return self

    def gte(self, column: str, value: Any):
        self._filters.append((column, "gte", value))
        return self

    def is_(self, column: str, value: Any):
        target = None if value in ("null", None) else value
        self._filters.append((column, "is", target))
        return self

    def order(self, column: str, desc: bool = False):
        self._order_by = (column, desc)
        return self

    def limit(self, value: int):
        self._limit = value
        return self

    # Operations
    def select(self, columns: Optional[str] = None, count: Optional[str] = None):
        self._operation = "select"
        self._count_mode = count
        return self

    def insert(self, data: Any):
        self._operation = "insert"
        self._payload = data if isinstance(data, list) else [data]
        return self

    def update(self, values: Dict[str, Any]):
        self._operation = "update"
        self._payload = values
        return self

    def upsert(self, data: Any):
        self._operation = "upsert"
        self._payload = data if isinstance(data, list) else [data]
        return self

    # Execution
    def execute(self) -> QueryResult:
        try:
            if self._operation == "select":
                return self._execute_select()
            if self._operation == "insert":
                return self._execute_insert()
            if self._operation == "update":
                return self._execute_update()
            if self._operation == "upsert":
                return self._execute_upsert()
            raise ValueError("Unsupported operation")
        finally:
            self.session.close()

    def _convert_value(self, column: str, value: Any):
        attr = getattr(self.model, column)
        try:
            python_type = attr.type.python_type
        except AttributeError:
            return value
        if python_type is datetime and isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value
        return value

    def _apply_filters(self, query):
        for column, op, value in self._filters:
            value = self._convert_value(column, value)
            attr = getattr(self.model, column)
            if op == "eq":
                query = query.filter(attr == value)
            elif op == "gte":
                query = query.filter(attr >= value)
            elif op == "is":
                query = query.filter(attr.is_(value))
        return query

    def _execute_select(self) -> QueryResult:
        query = self.session.query(self.model)
        query = self._apply_filters(query)
        if self._order_by:
            column, is_desc = self._order_by
            attr = getattr(self.model, column)
            query = query.order_by(desc_func(attr) if is_desc else asc(attr))
        if self._limit:
            query = query.limit(self._limit)
        rows = query.all()
        data = [row.to_dict() for row in rows]
        count = len(data) if self._count_mode == "exact" else None
        return QueryResult(data=data, count=count)

    def _execute_insert(self) -> QueryResult:
        rows = []
        for payload in self._payload:
            obj = self.model(**self._coerce_payload(payload))
            self.session.add(obj)
            rows.append(obj)
        self.session.commit()
        return QueryResult(data=[row.to_dict() for row in rows])

    def _execute_update(self) -> QueryResult:
        query = self.session.query(self.model)
        query = self._apply_filters(query)
        rows = query.all()
        for row in rows:
            for key, value in self._coerce_payload(self._payload).items():
                setattr(row, key, value)
        self.session.commit()
        return QueryResult(data=[row.to_dict() for row in rows])

    def _execute_upsert(self) -> QueryResult:
        saved = []
        for payload in self._payload:
            row_id = payload.get("id")
            instance = None
            if row_id:
                instance = self.session.get(self.model, row_id)
            if instance:
                for key, value in self._coerce_payload(payload).items():
                    setattr(instance, key, value)
            else:
                instance = self.model(**self._coerce_payload(payload))
                self.session.add(instance)
            saved.append(instance)
        self.session.commit()
        return QueryResult(data=[row.to_dict() for row in saved])

    def _coerce_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        coerced: Dict[str, Any] = {}
        for key, value in payload.items():
            if hasattr(self.model, key):
                attr = getattr(self.model, key)
                try:
                    python_type = attr.type.python_type
                except AttributeError:
                    python_type = None
                if python_type is datetime and isinstance(value, str):
                    try:
                        coerced[key] = datetime.fromisoformat(value)
                        continue
                    except ValueError:
                        pass
            coerced[key] = value
        return coerced


class LocalSupabaseClient:
    def __init__(self):
        self.models = TABLE_MODEL_MAP

    def table(self, name: str) -> LocalSupabaseQuery:
        if name not in self.models:
            raise ValueError(f"Unknown table '{name}'")
        return LocalSupabaseQuery(self.models[name])
