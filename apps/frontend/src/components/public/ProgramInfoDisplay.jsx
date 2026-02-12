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
    <article className="program-info" aria-label="Program information">
      <h1>{title}</h1>
      {description && <p className="program-description">{description}</p>}
      {eligibility && (
        <section aria-labelledby="eligibility-heading">
          <h2 id="eligibility-heading">Eligibility</h2>
          <p>{eligibility}</p>
        </section>
      )}
      {deadline_info && (
        <section aria-labelledby="deadline-heading">
          <h2 id="deadline-heading">Deadlines</h2>
          <p>{deadline_info}</p>
        </section>
      )}
      {(contact_email || contact_phone) && (
        <section aria-labelledby="contact-heading">
          <h2 id="contact-heading">Contact</h2>
          <ul>
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
