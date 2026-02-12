import React from 'react';

/**
 * Renders a list of resources with download links.
 * Uses storage backend URL when available; otherwise link to API download endpoint.
 */
export function ResourceDownloader({ resources = [] }) {
  if (!resources.length) return null;

  const getDownloadUrl = (resource) => {
    if (resource.url) return resource.url;
    if (resource.storage_key) {
      const base = import.meta.env.VITE_API_BASE_URL || '';
      return `${base.replace(/\/$/, '')}/api/public/resources/${encodeURIComponent(resource.storage_key)}`;
    }
    return null;
  };

  return (
    <section className="resource-downloads" aria-labelledby="resources-heading">
      <h2 id="resources-heading">Resources</h2>
      <ul>
        {resources.map((r) => {
          const url = getDownloadUrl(r);
          return (
            <li key={r.id}>
              {url ? (
                <a href={url} download target="_blank" rel="noopener noreferrer">
                  {r.label}
                </a>
              ) : (
                <span>{r.label}</span>
              )}
              {r.description && <span className="resource-desc"> — {r.description}</span>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
