"""Storage module for handling file storage (local or cloud)."""
from .local_storage import LocalStorage, get_local_storage

__all__ = ['LocalStorage', 'get_local_storage']
