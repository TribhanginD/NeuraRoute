"""
Base model with common fields and functionality
"""

import uuid
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel as PydanticBaseModel, Field
from sqlalchemy import Column, DateTime, func, String, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr, Session

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields"""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def to_json(self) -> Dict[str, Any]:
        """Convert model to JSON-serializable dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model"""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"


class BaseModelMixin:
    """Base model mixin with common fields and methods"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    # Common fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, **kwargs) -> None:
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    @classmethod
    def get_by_id(cls, db: Session, id: str):
        """Get model by ID"""
        return db.query(cls).filter(cls.id == id).first()
    
    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100):
        """Get all models with pagination"""
        return db.query(cls).offset(skip).limit(limit).all()
    
    @classmethod
    def create(cls, db: Session, **kwargs):
        """Create new model instance"""
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance
    
    def delete(self, db: Session) -> bool:
        """Delete model instance"""
        try:
            db.delete(self)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


# Pydantic base models
class BaseSchema(PydanticBaseModel):
    """Base Pydantic schema"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseCreateSchema(BaseSchema):
    """Base schema for creation"""
    pass


class BaseUpdateSchema(BaseSchema):
    """Base schema for updates"""
    pass


class BaseResponseSchema(BaseSchema):
    """Base schema for responses"""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp") 