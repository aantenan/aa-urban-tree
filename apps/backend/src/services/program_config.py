"""Load, cache, and serve program configuration for public listing (with cache invalidation)."""
import json
from pathlib import Path
from typing import Any

from models.program import ProgramConfig

_cache: ProgramConfig | None = None
_cache_etag: str | None = None


def _get_program_data_path() -> Path:
    from config import PROGRAM_DATA_PATH
    p = Path(PROGRAM_DATA_PATH)
    return p if p.is_absolute() else Path(__file__).resolve().parent.parent.parent.parent.parent / p


def _get_static_resources_path() -> Path:
    from config import STATIC_RESOURCES_PATH
    p = Path(STATIC_RESOURCES_PATH)
    return p if p.is_absolute() else Path(__file__).resolve().parent.parent.parent.parent.parent / p


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_program_config() -> ProgramConfig:
    """Load program config from JSON, merging with static resources. No auth required."""
    global _cache, _cache_etag
    data_path = _get_program_data_path()
    resources_path = _get_static_resources_path()
    data = _load_json(data_path)
    resources_data = _load_json(resources_path)
    # Merge storage_key from static_resources.mappings into program_data.resources by id
    mappings = resources_data.get("mappings") or {}
    for r in data.get("resources", []):
        if isinstance(r, dict) and r.get("id") in mappings:
            r["storage_key"] = mappings[r["id"]]
    # Append any mapping ids not already in resources
    for rid, storage_key in mappings.items():
        if not any(r.get("id") == rid for r in data.get("resources", [])):
            data.setdefault("resources", []).append({
                "id": rid,
                "label": rid.replace("_", " ").title(),
                "storage_key": storage_key,
            })
    config = ProgramConfig.model_validate(data)
    return config


def get_cached_program_config() -> tuple[ProgramConfig, str]:
    """
    Return cached program config and etag for conditional GET.
    Refreshes from disk when cache is empty or invalidated.
    """
    global _cache, _cache_etag
    if _cache is None:
        _cache = load_program_config()
        _cache_etag = str(hash(_cache.model_dump_json()))
    return _cache, _cache_etag or "0"


def invalidate_program_config_cache() -> None:
    """Clear cache so next request reloads from disk (for content updates)."""
    global _cache, _cache_etag
    _cache = None
    _cache_etag = None
