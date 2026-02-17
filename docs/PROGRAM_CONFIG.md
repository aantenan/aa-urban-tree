# Program Configuration and Content Management

Program information for the public listing page is stored as static JSON and served via the configuration API. Administrators can update program details without code changes.

## Configuration Files

- **`config/program_data.json`** — Program metadata, grant cycle dates, eligibility criteria, contact info
- **`config/static_resources.json`** — Mappings from resource IDs to storage keys for downloadable files

## API Endpoints

### `GET /api/config/program`

Returns complete program configuration for the public listing page. No authentication required.

**Response:** JSON with `program`, `grantCycle`, `eligibility`, `resources`, `title`, `description`, `deadlineInfo`.

**Cache:** Response includes `Cache-Control: public, max-age=300` (configurable via `PROGRAM_CONFIG_CACHE_MAX_AGE`).

### `GET /api/public/config`

Legacy endpoint; same data in original flat format. Kept for backward compatibility.

## Program Data Structure

```json
{
  "title": "Program title",
  "description": "Program description",
  "program": {
    "name": "...",
    "purpose": "...",
    "funding_available": 500000,
    "contact_email": "...",
    "contact_phone": null
  },
  "grant_cycle": {
    "year": 2025,
    "application_open": "2025-01-15",
    "application_deadline": "2025-06-30",
    "award_notification_date": "2025-08-15"
  },
  "eligibility_config": {
    "applicant_types": ["Municipalities", "..."],
    "project_types": ["Tree planting", "..."],
    "funding_limits": {"minimum": 5000, "maximum": 50000},
    "cost_match_requirement": 25,
    "ineligible_activities": ["..."]
  },
  "resources": [
    {"id": "...", "label": "...", "description": "...", "file_type": "PDF"}
  ]
}
```

## Static Resources

Resource files (PDFs, templates) are referenced by `storage_key`. The `static_resources.json` mappings merge storage keys into `program_data.resources` by `id`:

```json
{
  "mappings": {
    "application_guidelines": "public/guidelines/application-guidelines.pdf",
    "faq": "public/guidelines/faq.pdf"
  }
}
```

## Cache Invalidation

The program config is cached in memory. To reload after updating JSON files, restart the application or call `program_config.invalidate_program_config_cache()` (if exposed via an admin endpoint).

## Environment Variables

- `PROGRAM_DATA_PATH` — Path to program_data.json (default: `config/program_data.json`)
- `STATIC_RESOURCES_PATH` — Path to static_resources.json (default: `config/static_resources.json`)
- `PROGRAM_CONFIG_CACHE_MAX_AGE` — Cache max-age in seconds (default: 300)
