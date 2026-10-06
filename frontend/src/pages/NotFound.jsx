import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";

export default function NotFound() {
  return (
    <div className="auth-page">
      <EmptyState icon="🧭" title="Page not found" text="The page you are looking for does not exist.">
        <Link to="/dashboard" className="btn btn-primary">
          Back to Dashboard
        </Link>
      </EmptyState>
    </div>
  );
}
