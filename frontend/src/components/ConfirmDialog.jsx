import Modal from "./Modal";

export default function ConfirmDialog({ open, title, message, confirmText = "Confirm", loading, onConfirm, onCancel }) {
  return (
    <Modal open={open} title={title} onClose={loading ? undefined : onCancel}>
      <p className="muted">{message}</p>
      <div className="modal-actions">
        <button className="btn btn-outline" onClick={onCancel} disabled={loading}>
          Cancel
        </button>
        <button className="btn btn-primary" onClick={onConfirm} disabled={loading}>
          {loading && <span className="spinner sm" />} {confirmText}
        </button>
      </div>
    </Modal>
  );
}
