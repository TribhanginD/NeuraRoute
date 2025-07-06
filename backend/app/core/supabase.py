"""
Supabase client configuration for NeuraRoute
"""

import os
from typing import Optional
from supabase import create_client, Client
from .config import settings


class SupabaseManager:
    """Manages Supabase client connections"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get the main Supabase client (uses anon key)"""
        if self._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return self._client
    
    @property
    def admin_client(self) -> Client:
        """Get the admin Supabase client (uses service role key)"""
        if self._admin_client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
            self._admin_client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        return self._admin_client
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
    
    def is_admin_configured(self) -> bool:
        """Check if Supabase admin is properly configured"""
        return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY)


# Create global instance
supabase_manager = SupabaseManager()


def get_supabase_client() -> Client:
    """Get the main Supabase client"""
    return supabase_manager.client


def get_supabase_admin_client() -> Client:
    """Get the admin Supabase client"""
    return supabase_manager.admin_client


def is_supabase_configured() -> bool:
    """Check if Supabase is configured"""
    return supabase_manager.is_configured()


def is_supabase_admin_configured() -> bool:
    """Check if Supabase admin is configured"""
    return supabase_manager.is_admin_configured() 