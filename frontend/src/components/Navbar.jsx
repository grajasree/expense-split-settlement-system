import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ConfirmDialog from "./ConfirmDialog";

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [confirmOpen, setConfirmOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="navbar">
      <button className="icon-btn menu-btn" onClick={onMenuClick} aria-label="Open menu">
        ☰
      </button>
      <div className="brand">
        <span className="brand-logo">₹</span>
        <span className="brand-text">Expense Split</span>
      </div>
      <div className="navbar-right">
        <div className="user-chip">
          <span className="avatar">{user.name.charAt(0).toUpperCase()}</span>
          <div className="user-info">
            <strong>{user.name}</strong>
            <small>{user.email}</small>
          </div>
        </div>
        <button className="btn btn-outline btn-sm" onClick={() => setConfirmOpen(true)}>
          Logout
        </button>
      </div>
      <ConfirmDialog
        open={confirmOpen}
        title="Logout"
        message="Are you sure you want to log out?"
        confirmText="Logout"
        onConfirm={handleLogout}
        onCancel={() => setConfirmOpen(false)}
      />
    </header>
  );
}
