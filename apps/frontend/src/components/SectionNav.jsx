import React from 'react';

/**
 * Section-based navigation with completion status indicators.
 * sections: [{ id, label, href?, completed?: boolean }]
 */
export function SectionNav({ sections = [], currentId, className = '' }) {
  return (
    <nav aria-label="Section navigation" className={`section-nav ${className}`.trim()}>
      <ul className="section-nav__list">
        {sections.map((section) => {
          const isCurrent = section.id === currentId;
          const content = section.href ? (
            <a href={section.href} className="section-nav__link" aria-current={isCurrent ? 'step' : undefined}>
              {section.label}
              {section.completed != null && (
                <span className="section-nav__status" aria-hidden="true">
                  {section.completed ? ' ✓' : ''}
                </span>
              )}
            </a>
          ) : (
            <span className="section-nav__label" aria-current={isCurrent ? 'step' : undefined}>
              {section.label}
              {section.completed != null && (
                <span className="section-nav__status" aria-hidden="true">
                  {section.completed ? ' ✓' : ''}
                </span>
              )}
            </span>
          );
          return (
            <li key={section.id} className="section-nav__item">
              {content}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
