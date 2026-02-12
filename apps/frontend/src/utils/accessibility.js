/**
 * Accessibility utilities for WCAG 2.1: focus management and screen reader support.
 */

/**
 * Trap focus inside a container (e.g. modal). Call with ref to the container element.
 * Optional: focusFirst(el) to move focus to first focusable on open.
 */
export function getFocusableElements(container) {
  if (!container?.querySelector) return [];
  return Array.from(
    container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter((el) => !el.disabled && el.offsetParent !== null);
}

/**
 * Move focus to first focusable in container.
 */
export function focusFirst(container) {
  const els = getFocusableElements(container);
  if (els[0]) els[0].focus();
}

/**
 * Move focus to last focusable in container.
 */
export function focusLast(container) {
  const els = getFocusableElements(container);
  if (els.length) els[els.length - 1].focus();
}

/**
 * Create a focus trap: on Tab at last element go to first; on Shift+Tab at first go to last.
 * Returns cleanup function.
 */
export function trapFocus(container) {
  const handleKeyDown = (e) => {
    if (e.key !== 'Tab') return;
    const els = getFocusableElements(container);
    if (!els.length) return;
    const first = els[0];
    const last = els[els.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  };
  container?.addEventListener('keydown', handleKeyDown);
  return () => container?.removeEventListener('keydown', handleKeyDown);
}

/**
 * Announce to screen readers (live region). Use a dedicated aria-live element or inject one.
 */
export function announce(message, priority = 'polite') {
  const el = document.getElementById('sr-announcer') || createAnnouncer();
  el.setAttribute('aria-live', priority);
  el.textContent = '';
  requestAnimationFrame(() => {
    el.textContent = message;
  });
}

function createAnnouncer() {
  const el = document.createElement('div');
  el.id = 'sr-announcer';
  el.setAttribute('aria-live', 'polite');
  el.setAttribute('aria-atomic', 'true');
  el.className = 'sr-only';
  Object.assign(el.style, {
    position: 'absolute',
    width: '1px',
    height: '1px',
    padding: 0,
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0,0,0,0)',
    whiteSpace: 'nowrap',
    border: 0,
  });
  document.body.appendChild(el);
  return el;
}
