from typing import Optional

from .local_client import LocalSupabaseClient


class SupabaseClient:
    def __init__(self):
        self.client: Optional[LocalSupabaseClient] = LocalSupabaseClient()

    def get_client(self) -> LocalSupabaseClient:
        if not self.client:
            raise RuntimeError("Database client is not configured")
        return self.client

    def is_configured(self) -> bool:
        return self.client is not None


# Global instance using local SQL backend
supabase_client = SupabaseClient()


def get_supabase_client() -> LocalSupabaseClient:
    return supabase_client.get_client()


def is_supabase_configured() -> bool:
    return supabase_client.is_configured()
