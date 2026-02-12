import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Breadcrumb navigation. items: [{ label, path? }]. Current route can be last item without path.
 */
export function Breadcrumb({ items = [] }) {
  const location = useLocation();
  if (!items.length) return null;
  return (
    <nav aria-label="Breadcrumb" className="breadcrumb">
      <ol className="breadcrumb__list">
        {items.map((item, i) => {
          const isLast = i === items.length - 1;
          const isCurrent = isLast || item.path === location.pathname;
          return (
            <li key={i} className="breadcrumb__item">
              {item.path && !isCurrent ? (
                <Link to={item.path} className="breadcrumb__link">
                  {item.label}
                </Link>
              ) : (
                <span className="breadcrumb__current" aria-current={isCurrent ? 'page' : undefined}>
                  {item.label}
                </span>
              )}
              {!isLast && <span className="breadcrumb__sep" aria-hidden="true"> / </span>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
