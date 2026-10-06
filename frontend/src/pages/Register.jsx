import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../services/api";
import { isValidEmail } from "../utils/format";
import ErrorBanner from "../components/ErrorBanner";

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "" });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const validate = () => {
    const found = {};
    if (!form.name.trim()) found.name = "Name is required";
    if (!form.email.trim()) found.email = "Email is required";
    else if (!isValidEmail(form.email.trim())) found.email = "Enter a valid email address";
    if (!form.password) found.password = "Password is required";
    else if (form.password.length < 6) found.password = "Password must be at least 6 characters"; // same rule as backend
    if (form.confirm !== form.password) found.confirm = "Passwords do not match";
    return found;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setApiError("");
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length) return;

    setLoading(true);
    try {
      await register(form.name.trim(), form.email.trim(), form.password);
      navigate("/login", { replace: true, state: { registered: true } });
    } catch (error) {
      setApiError(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">₹</div>
        <h1>Create account</h1>
        <p className="muted">Start splitting expenses with your friends</p>
        <ErrorBanner message={apiError} />

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="name">Full name</label>
            <input id="name" placeholder="Your name" value={form.name} onChange={update("name")} />
            {errors.name && <span className="field-error">{errors.name}</span>}
          </div>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" placeholder="you@example.com" value={form.email} onChange={update("email")} />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" placeholder="At least 6 characters" value={form.password} onChange={update("password")} />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>
          <div className="field">
            <label htmlFor="confirm">Confirm password</label>
            <input id="confirm" type="password" placeholder="Re-enter password" value={form.confirm} onChange={update("confirm")} />
            {errors.confirm && <span className="field-error">{errors.confirm}</span>}
          </div>
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading && <span className="spinner sm" />} {loading ? "Creating account..." : "Register"}
          </button>
        </form>
        <p className="auth-switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
