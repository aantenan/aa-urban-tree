import React, { useEffect, useRef } from 'react';
import { trapFocus, focusFirst } from '../../utils/accessibility';

/**
 * Accessible modal: focus trap, escape to close, aria-modal and role="dialog".
 * onClose called on overlay click or Escape.
 */
export function Modal({
  open,
  onClose,
  title,
  'aria-labelledby': ariaLabelledby,
  'aria-describedby': ariaDescribedby,
  children,
  className = '',
}) {
  const overlayRef = useRef(null);
  const modalRef = useRef(null);
  const titleId = title ? 'modal-title' : undefined;

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose?.();
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    const el = modalRef.current ?? overlayRef.current;
    if (el) {
      focusFirst(el);
      const cleanup = trapFocus(el);
      return () => {
        cleanup?.();
        document.removeEventListener('keydown', handleKeyDown);
        document.body.style.overflow = '';
      };
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  if (!open) return null;

  const handleOverlayClick = (e) => {
    if (e.target === overlayRef.current) onClose?.();
  };

  return (
    <div
      ref={overlayRef}
      className={`modal-overlay ${className}`.trim()}
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={ariaLabelledby || titleId}
      aria-describedby={ariaDescribedby}
    >
      <div ref={modalRef} className="modal" onClick={(e) => e.stopPropagation()}>
        {title && (
          <h2 id={titleId} className="modal__title">
            {title}
          </h2>
        )}
        <div className="modal__content">{children}</div>
      </div>
    </div>
  );
}
