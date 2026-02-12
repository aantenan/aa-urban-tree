/**
 * Print and PDF utilities for confirmation receipts.
 * Uses window.print() for native print dialog (user can "Save as PDF").
 */

/**
 * Open print dialog for the current document. Optionally restrict to a selector.
 * Use a dedicated print stylesheet to hide nav/sidebar and show only receipt content.
 */
export function printReceipt(selector = null) {
  const el = selector ? document.querySelector(selector) : document.body;
  if (!el) return;
  const prevTitle = document.title;
  try {
    if (selector) {
      document.title = 'Confirmation receipt';
      const clone = el.cloneNode(true);
      const style = document.createElement('style');
      style.textContent = 'body * { visibility: hidden; } body .print-area, .print-area * { visibility: visible; } .print-area { position: absolute; left: 0; top: 0; width: 100%; }';
      document.body.appendChild(clone);
      clone.classList.add('print-area');
      window.print();
      clone.remove();
      style.remove();
    } else {
      window.print();
    }
  } finally {
    document.title = prevTitle;
  }
}

/**
 * Mark an element as the print area: add class "print-area" and use @media print in CSS
 * to show only that section when printing. Then call window.print() or printReceipt().
 */
export function getPrintStyles() {
  return `
    @media print {
      body * { visibility: hidden; }
      .print-area, .print-area * { visibility: visible; }
      .print-area { position: absolute; left: 0; top: 0; width: 100%; }
    }
  `;
}
