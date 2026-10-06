export default function ErrorBanner({ message, onRetry, type = "error" }) {
  if (!message) return null;
  return (
    <div className={`alert alert-${type}`} role="alert">
      <span>{message}</span>
      {onRetry && (
        <button className="btn btn-sm btn-outline" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
