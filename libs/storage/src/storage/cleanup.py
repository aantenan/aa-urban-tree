"""Utilities for removing orphaned files (e.g. not referenced in DB)."""
from storage.interfaces.base import StorageBackend


def delete_orphaned_keys(
    backend: StorageBackend,
    keys_to_delete: set[str],
) -> int:
    """
    Delete stored files by key. Use for orphan cleanup: pass keys that exist
    in storage but are no longer referenced in the database.
    Returns the number of files deleted.
    """
    deleted = 0
    for key in keys_to_delete:
        try:
            if backend.get_metadata(key) is not None:
                backend.delete(key)
                deleted += 1
        except Exception:
            pass
    return deleted
