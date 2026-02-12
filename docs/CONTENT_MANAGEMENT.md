# Content Management: Program Information & Static Resources

This document explains how to update program information and manage static resources for the **public listing** page without code changes.

## Overview

- **Program information** (title, description, eligibility, deadlines, contact) is stored in `config/program_data.json`.
- **Downloadable resources** (PDFs, templates, guidelines) are mapped in `config/static_resources.json` to storage keys. The actual files are stored via the storage backend (local or S3).

## Updating Program Information

1. Edit **`config/program_data.json`** in the repo.
2. Use valid JSON. Fields:
   - `title`, `description` (required / recommended)
   - `eligibility`, `deadline_info`, `contact_email`, `contact_phone` (optional)
   - `resources`: list of `{ "id", "label", "description?", "storage_key?", "url?" }`
   - `metadata`: optional `{ "last_updated", "version" }`
3. Validate before deploying:
   ```bash
   ./tools/scripts/update_program_data.sh
   ```
4. Deploy the updated file. The backend caches the config; **restart the backend** to pick up changes (or use cache invalidation if implemented).

## Managing Static Resources

1. **Add or replace files** in your storage (e.g. upload PDFs to the configured storage backend).
2. Edit **`config/static_resources.json`** and add or update entries under `"mappings"`:
   - Key: resource identifier (e.g. `application_guidelines`)
   - Value: storage key or path where the file is stored (e.g. `public/guidelines/application-guidelines.pdf`)
3. Ensure `config/program_data.json` has a `resources` entry with the same `id` and optional `storage_key` so the public page shows the link.

## Configuration

- **Backend env** (optional):
  - `PROGRAM_DATA_PATH`: path to program JSON (default `config/program_data.json`, relative to repo root)
  - `STATIC_RESOURCES_PATH`: path to resources mapping (default `config/static_resources.json`)
  - `PROGRAM_CONFIG_CACHE_MAX_AGE`: Cache-Control max-age in seconds (default `300`)

## Cache

The public config API (`GET /api/public/config`) sends `Cache-Control: public, max-age=...` so clients and CDNs can cache responses. After updating content, restart the backend to clear the in-memory cache and serve new data.
