import React from 'react';
import { Modal } from './Modal';
import { Button } from './Button';

/**
 * Confirmation modal with confirm/cancel. Use for destructive or important actions.
 * onConfirm and onCancel are called when user chooses; onClose on overlay/escape.
 */
export function ConfirmationDialog({
  open,
  onClose,
  onConfirm,
  onCancel,
  title = 'Confirm',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'primary',
  loading = false,
}) {
  const handleCancel = () => {
    onCancel?.();
    onClose?.();
  };
  const handleConfirm = async () => {
    await onConfirm?.();
    onClose?.();
  };
  return (
    <Modal open={open} onClose={handleCancel} title={title}>
      {message && <p className="modal__message">{message}</p>}
      <div className="confirmation-dialog__actions">
        <Button type="button" variant="secondary" onClick={handleCancel} disabled={loading}>
          {cancelLabel}
        </Button>
        <Button type="button" variant={variant} onClick={handleConfirm} loading={loading}>
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  );
}
