import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/dashboard", icon: "📊", label: "Dashboard" },
  { to: "/groups", icon: "👥", label: "Groups" },
  { to: "/expenses/new", icon: "➕", label: "Add Expense" },
  { to: "/expenses", icon: "🧾", label: "Expenses" },
  { to: "/balances", icon: "⚖️", label: "Balances" },
  { to: "/settlements", icon: "🤝", label: "Settlements" },
  { to: "/history", icon: "📈", label: "History & Reports" },
];

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {open && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <nav>
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/expenses"}
              onClick={onClose}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            >
              <span className="nav-icon">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">B.Tech Project<br />Expense Split & Settlement</div>
      </aside>
    </>
  );
}
