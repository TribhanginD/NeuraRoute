"""
Supabase service layer for database operations
"""

from typing import Dict, List, Optional, Any, Union
from supabase import Client
from ..core.supabase import get_supabase_client, get_supabase_admin_client
from ..core.logging import get_logger

logger = get_logger(__name__)


class SupabaseService:
    """Service class for Supabase operations"""
    
    def __init__(self, use_admin: bool = False):
        self.client: Client = get_supabase_admin_client() if use_admin else get_supabase_client()
        self.use_admin = use_admin
    
    async def get_all(self, table: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Get all records from a table with optional filters"""
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching from {table}: {str(e)}")
            return []
    
    async def get_by_id(self, table: str, record_id: Union[int, str]) -> Optional[Dict]:
        """Get a single record by ID"""
        try:
            response = self.client.table(table).select("*").eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error fetching record {record_id} from {table}: {str(e)}")
            return None
    
    async def create(self, table: str, data: Dict) -> Optional[Dict]:
        """Create a new record"""
        try:
            response = self.client.table(table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating record in {table}: {str(e)}")
            return None
    
    async def update(self, table: str, record_id: Union[int, str], data: Dict) -> Optional[Dict]:
        """Update a record by ID"""
        try:
            response = self.client.table(table).update(data).eq("id", record_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table}: {str(e)}")
            return None
    
    async def delete(self, table: str, record_id: Union[int, str]) -> bool:
        """Delete a record by ID"""
        try:
            response = self.client.table(table).delete().eq("id", record_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {table}: {str(e)}")
            return False
    
    async def get_summary(self, table: str) -> Dict:
        """Get summary statistics for a table"""
        try:
            # Get total count
            count_response = self.client.table(table).select("*", count="exact").execute()
            total_count = count_response.count if hasattr(count_response, 'count') else 0
            
            # Get recent records (last 10)
            recent_response = self.client.table(table).select("*").order("created_at", desc=True).limit(10).execute()
            recent_records = recent_response.data if recent_response.data else []
            
            return {
                "total_count": total_count,
                "recent_records": recent_records,
                "table": table
            }
        except Exception as e:
            logger.error(f"Error getting summary for {table}: {str(e)}")
            return {
                "total_count": 0,
                "recent_records": [],
                "table": table
            }
    
    async def search(self, table: str, search_term: str, columns: List[str]) -> List[Dict]:
        """Search records in specified columns"""
        try:
            query = self.client.table(table).select("*")
            
            # Build OR conditions for search
            for column in columns:
                query = query.or_(f"{column}.ilike.%{search_term}%")
            
            response = query.execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error searching in {table}: {str(e)}")
            return []
    
    async def get_paginated(self, table: str, page: int = 1, page_size: int = 20, 
                           filters: Optional[Dict] = None) -> Dict:
        """Get paginated results"""
        try:
            query = self.client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            response = query.range(offset, offset + page_size - 1).execute()
            
            return {
                "data": response.data if response.data else [],
                "page": page,
                "page_size": page_size,
                "has_more": len(response.data) == page_size if response.data else False
            }
        except Exception as e:
            logger.error(f"Error getting paginated results from {table}: {str(e)}")
            return {
                "data": [],
                "page": page,
                "page_size": page_size,
                "has_more": False
            }


# Create service instances
supabase_service = SupabaseService()
supabase_admin_service = SupabaseService(use_admin=True)


def get_supabase_service(use_admin: bool = False) -> SupabaseService:
    """Get Supabase service instance"""
    return supabase_admin_service if use_admin else supabase_service 