import React from 'react';

/**
 * Displays program information with structured formatting for the public listing.
 */
export function ProgramInfoDisplay({ config }) {
  if (!config) return null;
  const {
    title,
    description,
    eligibility,
    deadline_info,
    contact_email,
    contact_phone,
  } = config;

  return (
    <article className="program-info content-card" aria-label="Program information">
      <h2 className="program-info__title">{title}</h2>
      {description && <p className="program-info__description">{description}</p>}
      {eligibility && (
        <section className="program-info__section" aria-labelledby="eligibility-heading">
          <h3 id="eligibility-heading" className="program-info__heading">Eligibility</h3>
          <p className="program-info__text">{eligibility}</p>
        </section>
      )}
      {deadline_info && (
        <section className="program-info__section" aria-labelledby="deadline-heading">
          <h3 id="deadline-heading" className="program-info__heading">Deadlines</h3>
          <p className="program-info__text">{deadline_info}</p>
        </section>
      )}
      {(contact_email || contact_phone) && (
        <section className="program-info__section" aria-labelledby="contact-heading">
          <h3 id="contact-heading" className="program-info__heading">Contact</h3>
          <ul className="program-info__list">
            {contact_email && (
              <li>
                <a href={`mailto:${contact_email}`}>{contact_email}</a>
              </li>
            )}
            {contact_phone && <li>{contact_phone}</li>}
          </ul>
        </section>
      )}
    </article>
  );
}
