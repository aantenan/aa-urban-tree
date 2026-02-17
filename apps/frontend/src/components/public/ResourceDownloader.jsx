import React from 'react';

/**
 * Renders a list of resources with download links.
 * Uses storage backend URL when available; otherwise link to API download endpoint.
 */
export function ResourceDownloader({ resources = [] }) {
  if (!resources.length) return null;

  const getDownloadUrl = (resource) => {
    if (resource.url) return resource.url;
    const key = resource.storage_key || resource.storageKey;
    if (key) {
      const base = import.meta.env.VITE_API_BASE_URL || '';
      return `${base.replace(/\/$/, '')}/api/public/resources/${encodeURIComponent(key)}`;
    }
    return null;
  };

  return (
    <section className="resource-downloads content-card" aria-labelledby="resources-heading">
      <h2 id="resources-heading" className="resource-downloads__title">Resources</h2>
      <ul className="resource-downloads__list">
        {resources.map((r) => {
          const url = getDownloadUrl(r);
          return (
            <li key={r.id} className="resource-downloads__item">
              {url ? (
                <a href={url} download target="_blank" rel="noopener noreferrer" className="resource-downloads__link">
                  {r.label || r.title}
                </a>
              ) : (
                <span>{r.label}</span>
              )}
              {r.description && <span className="resource-downloads__desc"> — {r.description}</span>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
