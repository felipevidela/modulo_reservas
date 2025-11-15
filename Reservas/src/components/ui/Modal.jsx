import { useEffect } from 'react';

/**
 * Componente Modal reutilizable
 * @param {boolean} isOpen - Controla si el modal está visible
 * @param {function} onClose - Callback al cerrar el modal
 * @param {string} title - Título del modal
 * @param {node} children - Contenido del modal
 * @param {string} size - Tamaño del modal: 'sm', 'md', 'lg', 'xl'
 * @param {boolean} closeOnBackdrop - Si true, cierra al hacer click fuera del modal
 */
export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnBackdrop = true,
}) {
  // Cerrar con tecla Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'modal-sm',
    md: '',
    lg: 'modal-lg',
    xl: 'modal-xl'
  };

  const handleBackdropClick = (e) => {
    if (closeOnBackdrop && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="modal-backdrop fade show"
        style={{ zIndex: 1050 }}
        onClick={handleBackdropClick}
      ></div>

      {/* Modal */}
      <div
        className="modal fade show"
        style={{ display: 'block', zIndex: 1055 }}
        tabIndex="-1"
        role="dialog"
        aria-modal="true"
        onClick={handleBackdropClick}
      >
        <div className={`modal-dialog modal-dialog-centered ${sizeClasses[size]}`} role="document">
          <div className="modal-content">
            {/* Header */}
            {title && (
              <div className="modal-header">
                <h5 className="modal-title">{title}</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={onClose}
                  aria-label="Cerrar"
                ></button>
              </div>
            )}

            {/* Body */}
            <div className="modal-body">
              {children}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * Modal de Confirmación
 * Variante del Modal específica para confirmaciones
 */
export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = '¿Está seguro?',
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  confirmVariant = 'primary',
  isLoading = false,
}) {
  const handleConfirm = async () => {
    await onConfirm();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm" closeOnBackdrop={!isLoading}>
      <div className="mb-4">
        <p className="mb-0">{message}</p>
      </div>

      <div className="d-flex gap-2 justify-content-end">
        <button
          type="button"
          className="btn btn-outline-secondary"
          onClick={onClose}
          disabled={isLoading}
        >
          {cancelText}
        </button>
        <button
          type="button"
          className={`btn btn-${confirmVariant}`}
          onClick={handleConfirm}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              Procesando...
            </>
          ) : (
            confirmText
          )}
        </button>
      </div>
    </Modal>
  );
}
