"""
create_frontend.py  -  ONE file that creates the whole React frontend project.

HOW TO USE
  1. Put this file anywhere (for example next to your "backend" folder).
  2. Run:        python create_frontend.py
  3. A folder called "frontend" is created with every file inside it.
  4. Then:       cd frontend
                 npm install
                 npm run dev          (open http://localhost:5173)
  Start your Flask backend first:  python app.py   (http://127.0.0.1:5000)

The code of every file is written below between the ##### FILE: ... ##### lines,
so you can also read it here or copy any single file by hand.
"""
import os, sys

TARGET = "frontend"

BUNDLE = r'''
##### FILE: .env #####
# Copy this file to ".env" and change the URL only if your Flask backend runs somewhere else.
VITE_API_BASE_URL=http://127.0.0.1:5000
##### FILE: .env.example #####
# Copy this file to ".env" and change the URL only if your Flask backend runs somewhere else.
VITE_API_BASE_URL=http://127.0.0.1:5000
##### FILE: README.md #####
# Expense Split & Settlement System – Frontend

React + Vite + React Router + Axios + plain CSS.
Connects to the **existing, unmodified** Flask + MySQL backend:

`React (this project)  →  Flask REST API  →  MySQL`

## 1. Folder structure
```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── .env / .env.example          # backend URL
├── public/favicon.svg
└── src/
    ├── main.jsx                 # app entry (Router + providers)
    ├── App.jsx                  # all routes (public + protected)
    ├── index.css                # all styles (responsive)
    ├── services/api.js          # ★ ONLY file that calls the backend (Axios)
    ├── context/
    │   ├── AuthContext.jsx      # logged-in user, login / register / logout
    │   └── ToastContext.jsx     # success / error pop-up messages
    ├── hooks/
    │   ├── useUserGroups.js     # groups of the user
    │   ├── useSelectedGroup.js  # selected group kept in URL (?group=1)
    │   └── useAllGroupData.js   # expenses + balances + settlements of all groups
    ├── utils/format.js          # ₹ formatting, dates, CSV download
    ├── components/              # Navbar, Sidebar, Layout, ProtectedRoute, Modal,
    │                            # ConfirmDialog, Loader, EmptyState, StatCard, ...
    └── pages/
        ├── Login.jsx            ├── Register.jsx
        ├── Dashboard.jsx        ├── Groups.jsx        ├── GroupDetails.jsx
        ├── AddExpense.jsx       ├── Expenses.jsx
        ├── Balances.jsx         ├── Settlements.jsx   └── History.jsx
```

## 2. Installation
Requirements: **Node.js 18+** (check with `node -v`).
```bash
cd frontend
npm install
```
Packages used: `react`, `react-dom`, `react-router-dom`, `axios` (dev: `vite`, `@vitejs/plugin-react`).

## 3. Backend URL configuration
The URL is set in **one place** – the file `frontend/.env`:
```
VITE_API_BASE_URL=http://127.0.0.1:5000
```
Change it only if your Flask server runs on another host/port, then restart `npm run dev`.
(The backend already has `CORS(app)` enabled, so no backend change is needed.)

## 4. Start everything
**Terminal 1 – backend (your existing project, unchanged):**
```bash
cd backend
venv\Scripts\activate            # Windows   (Mac/Linux: source venv/bin/activate)
python app.py                    # runs on http://127.0.0.1:5000
```
**Terminal 2 – frontend:**
```bash
cd frontend
npm run dev                      # opens on http://localhost:5173
```
Production build (optional): `npm run build` → `dist/`.

## 5. API mapping (read from the backend source code)
| Feature | Backend endpoint | Method | Request body |
|---|---|---|---|
| Register | `/api/auth/register` | POST | `name, email, password` |
| Login | `/api/auth/login` | POST | `email, password` |
| List users | `/api/auth/users` | GET | – |
| Get user (session check) | `/api/auth/users/<id>` | GET | – |
| Create group | `/api/groups` | POST | `group_name, created_by` |
| My groups | `/api/groups/user/<user_id>` | GET | – |
| Group details + members | `/api/groups/<id>` | GET | – |
| Add member | `/api/groups/<id>/members` | POST | `user_id` **or** `email` |
| Add expense + split | `/api/expenses` | POST | `group_id, description, amount, paid_by, date, split_type` + `participants` (equal) or `splits[]` (percentage/custom) |
| Expense history of a group | `/api/expenses/group/<group_id>` | GET | – |
| One expense | `/api/expenses/<id>` | GET | – |
| Balances | `/api/settlements/balances/<group_id>` | GET | – |
| Who owes whom (preview) | `/api/settlements/suggest/<group_id>` | GET | – |
| Save settlements (pending) | `/api/settlements/generate/<group_id>` | POST | – |
| List settlements | `/api/settlements/group/<group_id>` | GET | – |
| Change settlement status | `/api/settlements/<id>/status` | PUT | `status` = `pending` \| `completed` |

All responses use `{ "success": true/false, "message": "...", "data": ... }`.
Split calculations (equal / percentage / custom, balances, who-owes-whom) are done **only by the backend**; the frontend sends the inputs and displays the backend's result.

## 6. How authentication works here
The backend has **no JWT / token / session** – `POST /api/auth/login` just returns the user (`id, name, email`).
So the frontend stores that user in `localStorage`, sends the `id` where the APIs need a user id, protects pages with a React Router `ProtectedRoute`, and re-checks the saved user on start-up with `GET /api/auth/users/<id>`.

## 7. Features NOT in the UI (because the backend has no such API)
I did not invent endpoints, so these are intentionally absent:
- **Remove member** – backend only has "add member".
- **Edit / Delete expense** – backend only has add + view.
- **Expense category** – the expense table has no category column.
- **Dashboard summary API** – the dashboard is built from the real group, expense, balance and settlement endpoints.
If you want these, add the endpoints to the Flask backend first and then a button can be wired to them in `src/services/api.js`.

## 8. How to test each module
Start backend + frontend, open http://localhost:5173.

**Register / Login**
1. Click *Create an account*. Try submitting empty → validation messages. Enter different passwords → "Passwords do not match".
2. Register `Alice / alice@example.com / alice123`, then `Bob` and `Charlie` the same way (log out between them).
3. Registering the same email again → backend error "Email is already registered".
4. Login with a wrong password → "Invalid email or password". Login correctly → Dashboard. Open `/balances` while logged out → redirected to Login. Use **Logout** (top right).

**Groups**
1. Sidebar → *Groups* → *Create Group* → "Goa Trip" (you become a member automatically).
2. Open *View Details* → *Add member*: pick Bob from the list, then add Charlie by typing his email. Members table updates.
3. Adding the same person again → "User is already a member of this group".

**Expenses**
1. Sidebar → *Add Expense*, choose "Goa Trip", fill description, amount, date, *Paid by*.
2. Submit → a result screen appears. Then open *Expenses* → *View split* to see each person's share.
3. Empty description or amount `0` → error messages.

**Split**
- *Equal*: untick a member to exclude them → backend divides among the ticked ones (e.g. ₹100 among 3 → 33.34 / 33.33 / 33.33).
- *Percentage*: enter 50 / 30 / 20 → green chip "100%". Enter 50 / 30 / 10 → blocked: "Percentages add up to 90%".
- *Custom amount*: for ₹900 enter 500 / 300 / 100 → OK. Enter amounts that don't add up → blocked with the difference shown.
- The shares shown after saving are **the numbers returned by the backend**.

**Balance**
1. Sidebar → *Balances*, choose the group.
2. Check cards (You paid / Your share / Net balance) and the table: Total paid, Total owed, Net, To receive, To pay, Status badge.

**Settlement**
1. Sidebar → *Settlements* → see **Who owes whom** (e.g. "Bob owes Alice ₹1,600").
2. Click *Save as pending settlements* → confirm → rows appear with status *pending*.
3. Click *Mark completed* → confirm → status changes; go back to *Balances* to see the net balances reduce.
4. Use the All / Pending / Completed tabs to filter.

**History & Reports**
1. Sidebar → *History & Reports*.
2. *Expense History*: search text, filter by group and date range, *Export CSV*.
3. *Settlement History*: filter by group and status. *Group-wise Report*: total spent / pending / completed per group.

**Error handling check**: stop the Flask server and reload any page → "Cannot reach the backend at http://127.0.0.1:5000 ...".
##### FILE: index.html #####
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Expense Split & Settlement System</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
##### FILE: package.json #####
{
  "name": "expense-split-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.2",
    "vite": "^5.4.8"
  }
}
##### FILE: vite.config.js #####
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
});
##### FILE: public/favicon.svg #####
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" xmlns:c2pa="http://c2pa.org/manifest"><metadata><c2pa:manifest>AAAWgmp1bWIAAAAeanVtZGMycGEAEQAQgAAAqgA4m3EDYzJwYQAAABZcanVtYgAAAEdqdW1kYzJtYQARABCAAACqADibcQN1cm46YzJwYTo2NDU1NGNhZi0wZmRkLTQ0MzgtYWNkOC1lMmU3ZDIyZjFmZmEAAAADl2p1bWIAAAApanVtZGMyYXMAEQAQgAAAqgA4m3EDYzJwYS5hc3NlcnRpb25zAAAAALxqdW1iAAAARGp1bWRjYm9yABEAEIAAAKoAOJtxE2MycGEuaW5ncmVkaWVudC52MwAAAAAYYzJzaHtsWSf4MkaD566GsvwZumMAAABwY2JvcqNpZGM6Zm9ybWF0bWltYWdlL3N2Zyt4bWxqaW5zdGFuY2VJRHgseG1wOmlpZDphY2ExZjM1MS1iNmQ5LTRmZjQtODhjYy03ZDhkMjE2YzEzNWNscmVsYXRpb25zaGlwaHBhcmVudE9mAAAB4mp1bWIAAABBanVtZGNib3IAEQAQgAAAqgA4m3ETYzJwYS5hY3Rpb25zLnYyAAAAABhjMnNoEwPyHS0NPb5malRPFxmCoAAAAZljYm9yomdhY3Rpb25zgqJmYWN0aW9ua2MycGEub3BlbmVkanBhcmFtZXRlcnOha2luZ3JlZGllbnRzgaJjdXJseC1zZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmluZ3JlZGllbnQudjNkaGFzaFggbbp9LAx2e/UJVHA9PL/27P1fbcvZZ0cpD43tEv4FSGCkZmFjdGlvbngdY29tLmFudGhyb3BpYy5jbGF1ZGUucHJvdmlkZWRqcGFyYW1ldGVyc6F4H2NvbS5hbnRocm9waWMub3JpZ2luLWNvbmZpZGVuY2VndW5rbm93bmtkZXNjcmlwdGlvbnhmQ2xhdWRlIHByb3ZpZGVkIHRoaXMgZmlsZSBhdCB0aGUgcmVxdWVzdCBvZiBhIHVzZXIgYW5kIG1heSBoYXZlIGNyZWF0ZWQgb3IgbW9kaWZpZWQgdGhlIGZpbGUgY29udGVudHMubXNvZnR3YXJlQWdlbnShZG5hbWVmQ2xhdWRlcmFsbEFjdGlvbnNJbmNsdWRlZPUAAADIanVtYgAAAEBqdW1kY2JvcgARABCAAACqADibcRNjMnBhLmhhc2guZGF0YQAAAAAYYzJzaJUj8f6EC/oXTNq/LcvEfnwAAACAY2JvcqVjYWxnZnNoYTI1NmNwYWRNAAAAAAAAAAAAAAAAAGRoYXNoWCBLTGjyGI1Oa6FAedW7LIvDYpINPbUKt2T0sm2Y8sK5YWRuYW1lbmp1bWJmIG1hbmlmZXN0amV4Y2x1c2lvbnOBomVzdGFydBh7Zmxlbmd0aBkeBAAAAj5qdW1iAAAAJ2p1bWRjMmNsABEAEIAAAKoAOJtxA2MycGEuY2xhaW0udjIAAAACD2Nib3KlY2FsZ2ZzaGEyNTZpc2lnbmF0dXJleE1zZWxmI2p1bWJmPS9jMnBhL3VybjpjMnBhOjY0NTU0Y2FmLTBmZGQtNDQzOC1hY2Q4LWUyZTdkMjJmMWZmYS9jMnBhLnNpZ25hdHVyZWppbnN0YW5jZUlEeCx4bXA6aWlkOjYzYjQ4YjRiLWI3NjctNDA2Ni04MmUxLTNjMWI0MzZjYzc0ZHJjcmVhdGVkX2Fzc2VydGlvbnODomN1cmx4LXNlbGYjanVtYmY9YzJwYS5hc3NlcnRpb25zL2MycGEuaW5ncmVkaWVudC52M2RoYXNoWCBtun0sDHZ79QlUcD08v/bs/V9ty9lnRykPje0S/gVIYKJjdXJseCpzZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmFjdGlvbnMudjJkaGFzaFggCt86TaqK1nTG75ZxhNB5MWv6avjhjILvoHnqE5U4Mg+iY3VybHgpc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5oYXNoLmRhdGFkaGFzaFgg4QUjyqm2CilOEy6MzahdRIk+1BL9cEIuffyb84aat8F0Y2xhaW1fZ2VuZXJhdG9yX2luZm+jZG5hbWVvQW50aHJvcGljIEZpbGVzZ3ZlcnNpb25lMS4wLjBrc3BlY1ZlcnNpb25lMi40LjAAABA4anVtYgAAAChqdW1kYzJjcwARABCAAACqADibcQNjMnBhLnNpZ25hdHVyZQAAABAIY2JvctKEWQISogEmGCFZAgowggIGMIIBjaADAgECAhRA5aAK7sI50L64g/oGQgU9Z1UTADAKBggqhkjOPQQDAzBJMRcwFQYDVQQKEw5BbnRocm9waWMsIFBCQzEuMCwGA1UEAxMlQW50aHJvcGljIENvbnRlbnQgQ3JlZGVudGlhbHMgUm9vdCBDQTAeFw0yNjA4MDcxODQzNTZaFw0yODA4MDYxOTQzNTZaMEQxFzAVBgNVBAoTDkFudGhyb3BpYywgUEJDMSkwJwYDVQQDEyBBbnRocm9waWMgQ2xhdWRlIENvbnRlbnQgU2lnbmluZzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJh6CmvLUBgFFNU0vUKlOVtE6djd17L5SuwX0LemFisBM3dkd/3cyjxFA3Qo5S46fX0/ihY0VZ7mfb9KF703t5OjWDBWMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUEDjAMBgorBgEEAYPoXgIBMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUzlHiBIFOZFsj+OPEz5o+nMHXXMIwCgYIKoZIzj0EAwMDZwAwZAIwMXMdFJ4BetLLVY7ORuE9noqbbAZOZn/aArXyTwFAZfKrPzxF2vPoJNf1+UCdg1XGAjBwX1zd9WGqYkqmL5SFqw1QySjr1zJfpJM9+1rdDwSPLMOPOjKuiXjoU/pUUeG9RwmhY3BhZFkNngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPZYQCKc/6lJ158bE/QN+xaIY4hWElN1Ial+Q0/MI4sWhXTOEeN1zEBe7IKXRQ6K0iY3k9FM/aaVzo2AU4nnozIiUXo=</c2pa:manifest></metadata><rect width="64" height="64" rx="14" fill="#4f46e5"/><text x="32" y="43" font-size="32" text-anchor="middle" fill="#fff" font-family="Arial" font-weight="700">₹</text></svg>
##### FILE: src/App.jsx #####
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Groups from "./pages/Groups";
import GroupDetails from "./pages/GroupDetails";
import AddExpense from "./pages/AddExpense";
import Expenses from "./pages/Expenses";
import Balances from "./pages/Balances";
import Settlements from "./pages/Settlements";
import History from "./pages/History";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      {/* public pages */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* pages that need a logged-in user */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/groups" element={<Groups />} />
        <Route path="/groups/:groupId" element={<GroupDetails />} />
        <Route path="/expenses/new" element={<AddExpense />} />
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/balances" element={<Balances />} />
        <Route path="/settlements" element={<Settlements />} />
        <Route path="/history" element={<History />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
##### FILE: src/components/ConfirmDialog.jsx #####
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
##### FILE: src/components/EmptyState.jsx #####
export default function EmptyState({ icon = "📭", title, text, children }) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      {text && <p>{text}</p>}
      {children}
    </div>
  );
}
##### FILE: src/components/ErrorBanner.jsx #####
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
##### FILE: src/components/GroupSelect.jsx #####
export default function GroupSelect({ groups, value, onChange, label = "Group" }) {
  return (
    <label className="group-select">
      <span>{label}</span>
      <select value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
        {groups.map((group) => (
          <option key={group.id} value={group.id}>
            {group.group_name}
          </option>
        ))}
      </select>
    </label>
  );
}
##### FILE: src/components/Layout.jsx #####
import { useState } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="app-shell">
      <Navbar onMenuClick={() => setSidebarOpen((open) => !open)} />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
##### FILE: src/components/Loader.jsx #####
export default function Loader({ text = "Loading..." }) {
  return (
    <div className="loader-box">
      <span className="spinner" />
      <p>{text}</p>
    </div>
  );
}
##### FILE: src/components/Modal.jsx #####
export default function Modal({ open, title, onClose, children }) {
  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <div className="modal-head">
          <h3>{title}</h3>
          <button className="icon-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
##### FILE: src/components/Navbar.jsx #####
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
##### FILE: src/components/NoGroups.jsx #####
import { Link } from "react-router-dom";
import EmptyState from "./EmptyState";

export default function NoGroups() {
  return (
    <EmptyState icon="👥" title="No groups yet" text="Create a group (or ask a friend to add you) to get started.">
      <Link to="/groups" className="btn btn-primary">
        Go to Groups
      </Link>
    </EmptyState>
  );
}
##### FILE: src/components/PageHeader.jsx #####
export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      <div className="page-header-actions">{children}</div>
    </div>
  );
}
##### FILE: src/components/ProtectedRoute.jsx #####
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Loader from "./Loader";

/** Only lets logged-in users see the page; others are sent to /login. */
export default function ProtectedRoute({ children }) {
  const { user, checking } = useAuth();
  const location = useLocation();

  if (checking) return <Loader text="Checking your session..." />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  return children;
}
##### FILE: src/components/Sidebar.jsx #####
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
##### FILE: src/components/StatCard.jsx #####
export default function StatCard({ icon, label, value, tone = "primary", hint }) {
  return (
    <div className={`stat-card tone-${tone}`}>
      <div className="stat-icon">{icon}</div>
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
        {hint && <div className="stat-hint">{hint}</div>}
      </div>
    </div>
  );
}
##### FILE: src/components/StatusBadge.jsx #####
/** Works for settlement status (pending/completed) and balance status (gets back/owes/settled). */
const TONES = {
  pending: "amber",
  completed: "green",
  "gets back": "green",
  owes: "red",
  settled: "gray",
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${TONES[status] || "gray"}`}>{status}</span>;
}
##### FILE: src/context/AuthContext.jsx #####
/**
 * AuthContext - keeps the logged-in user.
 * The backend does not issue tokens, so after a successful login we keep the
 * returned user ({id, name, email}) in localStorage and use it for all API calls.
 * On start-up we re-check the user with GET /api/auth/users/<id>.
 */
import { createContext, useContext, useEffect, useState } from "react";
import { getUser, loginUser, registerUser } from "../services/api";

const STORAGE_KEY = "expense_split_user";
const AuthContext = createContext(null);

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);
  const [checking, setChecking] = useState(Boolean(readStoredUser()));

  // Make sure the saved user still exists in the database
  useEffect(() => {
    if (!user) {
      setChecking(false);
      return;
    }
    getUser(user.id)
      .catch((error) => {
        if (error?.response?.status === 404) logout(); // user no longer exists
      })
      .finally(() => setChecking(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email, password) => {
    const response = await loginUser({ email, password });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(response.data));
    setUser(response.data);
    return response;
  };

  const register = (name, email, password) => registerUser({ name, email, password });

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, checking, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
##### FILE: src/context/ToastContext.jsx #####
import { createContext, useCallback, useContext, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = "success") => {
    const id = Date.now() + Math.random();
    setToasts((list) => [...list, { id, message, type }]);
    setTimeout(() => setToasts((list) => list.filter((t) => t.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.type}`}>
            {toast.type === "success" ? "✔ " : "⚠ "}
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
##### FILE: src/hooks/useAllGroupData.js #####
import { useCallback, useEffect, useState } from "react";
import {
  getUserGroups,
  getGroupExpenses,
  getBalances,
  getGroupSettlements,
  getErrorMessage,
} from "../services/api";

/**
 * Loads, for every group of the user, the real data from the backend:
 * expenses, balances and settlements. Used by Dashboard and History pages.
 */
export default function useAllGroupData(userId) {
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  const reload = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const groups = (await getUserGroups(userId)).data;
      const items = await Promise.all(
        groups.map(async (group) => {
          const [exp, bal, set] = await Promise.all([
            getGroupExpenses(group.id),
            getBalances(group.id),
            getGroupSettlements(group.id),
          ]);
          return {
            group,
            expenses: exp.data.expenses,
            totalSpent: exp.data.total_spent,
            balances: bal.data.balances,
            settlements: set.data.settlements,
          };
        })
      );
      setState({ loading: false, error: "", items });
    } catch (err) {
      setState({ loading: false, error: getErrorMessage(err), items: [] });
    }
  }, [userId]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { ...state, reload };
}
##### FILE: src/hooks/useSelectedGroup.js #####
import { useSearchParams } from "react-router-dom";

/**
 * Keeps the selected group in the URL (?group=3) so links like
 * "/balances?group=3" open the right group directly.
 */
export default function useSelectedGroup(groups) {
  const [params, setParams] = useSearchParams();
  const fromUrl = Number(params.get("group")) || null;
  const selected = groups.some((g) => g.id === fromUrl) ? fromUrl : groups[0]?.id ?? null;

  const select = (id) => setParams(id ? { group: String(id) } : {}, { replace: true });
  return [selected, select];
}
##### FILE: src/hooks/useUserGroups.js #####
import { useCallback, useEffect, useState } from "react";
import { getUserGroups, getErrorMessage } from "../services/api";

/** Loads the groups the logged-in user belongs to. */
export default function useUserGroups(userId) {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await getUserGroups(userId);
      setGroups(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { groups, loading, error, reload };
}
##### FILE: src/index.css #####
/* ============================================================
   Expense Split & Settlement System - Styles
   ============================================================ */
:root {
  --primary: #4f46e5;
  --primary-dark: #4338ca;
  --primary-soft: #eef2ff;
  --bg: #f4f6fb;
  --card: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --border: #e5e7eb;
  --green: #059669;
  --green-soft: #d1fae5;
  --red: #dc2626;
  --red-soft: #fee2e2;
  --amber: #d97706;
  --amber-soft: #fef3c7;
  --blue: #2563eb;
  --blue-soft: #dbeafe;
  --purple: #7c3aed;
  --purple-soft: #ede9fe;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(16, 24, 40, 0.08), 0 1px 2px rgba(16, 24, 40, 0.04);
  --nav-h: 64px;
  --side-w: 240px;
}

* { box-sizing: border-box; }
html, body, #root { height: 100%; }
body {
  margin: 0;
  font-family: "Inter", "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  line-height: 1.5;
}
h1, h2, h3 { margin: 0; line-height: 1.25; }
h1 { font-size: 1.6rem; }
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }
.muted { color: var(--muted); }
.small { font-size: 0.85rem; }
.center { text-align: center; }
.text-green { color: var(--green); font-weight: 600; }
.text-red { color: var(--red); font-weight: 600; }
p { margin: 0.25rem 0; }

/* ---------- App shell ---------- */
.app-shell { min-height: 100%; }
.navbar {
  position: fixed; top: 0; left: 0; right: 0; height: var(--nav-h); z-index: 30;
  display: flex; align-items: center; gap: 12px; padding: 0 20px;
  background: #fff; border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.1rem; }
.brand-logo {
  width: 36px; height: 36px; border-radius: 10px; background: var(--primary); color: #fff;
  display: grid; place-items: center; font-size: 1.2rem;
}
.navbar-right { margin-left: auto; display: flex; align-items: center; gap: 14px; }
.user-chip { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%; background: var(--primary-soft); color: var(--primary);
  display: grid; place-items: center; font-weight: 700;
}
.user-info { display: flex; flex-direction: column; line-height: 1.2; }
.user-info small { color: var(--muted); }
.menu-btn { display: none; }

.sidebar {
  position: fixed; top: var(--nav-h); bottom: 0; left: 0; width: var(--side-w); z-index: 20;
  background: #111827; color: #d1d5db; padding: 16px 12px; display: flex; flex-direction: column;
  overflow-y: auto;
}
.sidebar nav { display: flex; flex-direction: column; gap: 4px; }
.nav-link {
  display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 10px;
  color: #d1d5db; font-weight: 500;
}
.nav-link:hover { background: #1f2937; text-decoration: none; color: #fff; }
.nav-link.active { background: var(--primary); color: #fff; }
.nav-icon { width: 22px; text-align: center; }
.sidebar-footer { margin-top: auto; padding: 12px; font-size: 0.75rem; color: #6b7280; }
.sidebar-overlay { display: none; }

.content { margin-left: var(--side-w); padding: calc(var(--nav-h) + 24px) 28px 40px; max-width: 1400px; }

/* ---------- Page header ---------- */
.page-header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
.page-header-actions { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; }
.section-title { margin: 22px 0 10px; font-size: 1.05rem; }

/* ---------- Cards ---------- */
.card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow); padding: 20px; margin-bottom: 20px;
}
.card-title { font-size: 1.05rem; margin-bottom: 14px; }
.card-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.card-head .card-title { margin-bottom: 0; }
.two-col { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
.two-col .card { margin-bottom: 0; }
.two-col { margin-bottom: 20px; }

.grid-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 20px; }
.stat-card {
  display: flex; gap: 14px; align-items: center; background: #fff; border: 1px solid var(--border);
  border-radius: var(--radius); padding: 18px; box-shadow: var(--shadow);
}
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center; font-size: 1.4rem; background: var(--primary-soft); flex-shrink: 0; }
.stat-label { color: var(--muted); font-size: 0.85rem; }
.stat-value { font-size: 1.35rem; font-weight: 700; }
.stat-hint { font-size: 0.78rem; color: var(--muted); }
.tone-green .stat-icon { background: var(--green-soft); } .tone-green .stat-value { color: var(--green); }
.tone-red .stat-icon { background: var(--red-soft); } .tone-red .stat-value { color: var(--red); }
.tone-amber .stat-icon { background: var(--amber-soft); }
.tone-blue .stat-icon { background: var(--blue-soft); }
.tone-purple .stat-icon { background: var(--purple-soft); }

.quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
.quick-action {
  display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 16px 10px;
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius); color: var(--text);
  font-weight: 600; box-shadow: var(--shadow); transition: transform .15s, border-color .15s;
}
.quick-action span { font-size: 1.5rem; }
.quick-action:hover { transform: translateY(-2px); border-color: var(--primary); text-decoration: none; }

/* ---------- Groups ---------- */
.grid-groups { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 16px; }
.group-card { margin-bottom: 0; text-align: center; }
.group-avatar {
  width: 56px; height: 56px; margin: 0 auto 10px; border-radius: 16px; background: var(--primary-soft);
  color: var(--primary); display: grid; place-items: center; font-size: 1.5rem; font-weight: 700;
}
.group-card-actions { display: flex; justify-content: center; gap: 8px; margin-top: 14px; flex-wrap: wrap; }

/* ---------- Buttons ---------- */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer;
  padding: 10px 18px; border-radius: 9px; border: 1px solid transparent; font-size: 0.95rem; font-weight: 600;
  font-family: inherit; transition: background .15s, opacity .15s;
}
.btn:hover { text-decoration: none; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--primary-dark); }
.btn-outline { background: #fff; color: var(--text); border-color: var(--border); }
.btn-outline:hover:not(:disabled) { background: #f9fafb; }
.btn-success { background: var(--green); color: #fff; }
.btn-sm { padding: 6px 12px; font-size: 0.85rem; }
.btn-block { width: 100%; }
.icon-btn { background: none; border: none; font-size: 1.25rem; cursor: pointer; padding: 6px 10px; border-radius: 8px; color: var(--text); }
.icon-btn:hover { background: #f3f4f6; }
.row-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }

/* ---------- Forms ---------- */
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.field label, .group-select span, .inline-field { font-size: 0.85rem; font-weight: 600; color: #374151; }
input, select {
  font-family: inherit; font-size: 0.95rem; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 9px;
  background: #fff; color: var(--text); width: 100%;
}
input:focus, select:focus { outline: 2px solid var(--primary-soft); border-color: var(--primary); }
.field-error { color: var(--red); font-size: 0.82rem; }
.field-error.block { display: block; margin-top: 8px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 18px; }
.span-2 { grid-column: span 2; }
.form-card { max-width: 820px; }
.group-select { display: flex; flex-direction: column; gap: 4px; min-width: 200px; }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
.toolbar.card { padding: 14px 16px; }
.toolbar input, .toolbar select { width: auto; flex: 1 1 160px; }
.toolbar .search { flex: 2 1 240px; }
.inline-field { display: flex; align-items: center; gap: 6px; }
.inline-field input { width: auto; }

/* split section */
.tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.tab { padding: 8px 16px; border-radius: 999px; border: 1px solid var(--border); background: #fff; cursor: pointer; font-weight: 600; font-family: inherit; color: var(--muted); }
.tab.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.tabs.compact .tab { padding: 5px 12px; font-size: 0.85rem; }
.split-list { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
.split-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 14px; border: 1px solid var(--border); border-radius: 10px; background: #fafbff; }
.check { display: flex; align-items: center; gap: 10px; cursor: pointer; font-weight: 500; }
.check input { width: 18px; height: 18px; }
.input-suffix { display: flex; align-items: center; gap: 6px; width: 150px; }
.input-suffix em { font-style: normal; color: var(--muted); font-weight: 600; }
.total-chip { display: inline-block; margin-top: 12px; padding: 6px 14px; border-radius: 999px; font-weight: 600; font-size: 0.9rem; }
.total-chip.ok { background: var(--green-soft); color: var(--green); }
.total-chip.bad { background: var(--amber-soft); color: var(--amber); }

/* ---------- Tables ---------- */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
th { text-align: left; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); padding: 10px 12px; border-bottom: 1px solid var(--border); white-space: nowrap; }
td { padding: 12px; border-bottom: 1px solid #f1f2f6; vertical-align: middle; }
tbody tr:hover { background: #fafbff; }
tfoot td { font-weight: 700; border-top: 2px solid var(--border); border-bottom: none; }
.num { text-align: right !important; white-space: nowrap; }
.me-row { background: var(--primary-soft); }
.detail-row td { background: #fafbff; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: #fff; border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; font-size: 0.85rem; }
.bar-cell { display: flex; align-items: center; gap: 10px; min-width: 200px; }
.bar { flex: 1; height: 8px; background: #eef0f6; border-radius: 99px; overflow: hidden; min-width: 80px; }
.bar div { height: 100%; background: var(--primary); border-radius: 99px; }

.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; text-transform: capitalize; }
.badge-green { background: var(--green-soft); color: var(--green); }
.badge-red { background: var(--red-soft); color: var(--red); }
.badge-amber { background: var(--amber-soft); color: var(--amber); }
.badge-blue { background: var(--blue-soft); color: var(--blue); }
.badge-gray { background: #e5e7eb; color: #4b5563; }

/* who owes whom */
.owe-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.owe-list li { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 14px 16px; border: 1px solid var(--border); border-radius: 10px; background: #fafbff; }
.owe-from { font-weight: 700; color: var(--red); }
.owe-to { font-weight: 700; color: var(--green); }
.owe-arrow { color: var(--muted); }
.owe-amount { margin-left: auto; font-size: 1.1rem; }

/* ---------- Feedback ---------- */
.alert { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 10px; margin-bottom: 16px; font-size: 0.92rem; }
.alert-error { background: var(--red-soft); color: #991b1b; border: 1px solid #fecaca; }
.alert-success { background: var(--green-soft); color: #065f46; border: 1px solid #a7f3d0; }
.loader-box { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 60px 0; color: var(--muted); }
.spinner { width: 34px; height: 34px; border: 3px solid #e0e7ff; border-top-color: var(--primary); border-radius: 50%; animation: spin .8s linear infinite; display: inline-block; }
.spinner.sm { width: 14px; height: 14px; border-width: 2px; border-color: rgba(255,255,255,.5); border-top-color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { text-align: center; padding: 36px 16px; color: var(--muted); }
.empty-icon { font-size: 2.4rem; }
.empty h3 { color: var(--text); margin: 8px 0 4px; }
.empty .btn { margin-top: 14px; }

.toast-container { position: fixed; top: 76px; right: 20px; z-index: 100; display: flex; flex-direction: column; gap: 10px; }
.toast { padding: 12px 18px; border-radius: 10px; box-shadow: 0 6px 20px rgba(0,0,0,.15); color: #fff; font-weight: 500; animation: slide .25s ease; max-width: 340px; }
.toast-success { background: var(--green); }
.toast-error { background: var(--red); }
@keyframes slide { from { transform: translateX(30px); opacity: 0; } to { transform: none; opacity: 1; } }

.modal-backdrop { position: fixed; inset: 0; background: rgba(17,24,39,.5); z-index: 90; display: grid; place-items: center; padding: 16px; }
.modal { background: #fff; border-radius: 14px; padding: 22px; width: 100%; max-width: 440px; box-shadow: 0 20px 50px rgba(0,0,0,.25); }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }

/* ---------- Login / Register ---------- */
.auth-page { min-height: 100%; display: grid; place-items: center; padding: 24px; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 60%, #2563eb 100%); }
.auth-card { width: 100%; max-width: 420px; background: #fff; border-radius: 18px; padding: 32px 28px; box-shadow: 0 20px 50px rgba(0,0,0,.25); }
.auth-card h1 { text-align: center; }
.auth-card > .muted { text-align: center; margin-bottom: 18px; }
.auth-logo { width: 56px; height: 56px; margin: 0 auto 12px; border-radius: 16px; background: var(--primary); color: #fff; display: grid; place-items: center; font-size: 1.7rem; font-weight: 700; }
.auth-switch { text-align: center; margin-top: 16px; color: var(--muted); }
.auth-page .empty { background: #fff; border-radius: 16px; }

/* ---------- Responsive ---------- */
@media (max-width: 960px) {
  .menu-btn { display: inline-block; }
  .sidebar { transform: translateX(-100%); transition: transform .25s; box-shadow: 4px 0 20px rgba(0,0,0,.2); }
  .sidebar.open { transform: none; }
  .sidebar-overlay { display: block; position: fixed; inset: 0; top: var(--nav-h); background: rgba(0,0,0,.4); z-index: 15; }
  .content { margin-left: 0; padding: calc(var(--nav-h) + 18px) 16px 32px; }
  .two-col { grid-template-columns: 1fr; }
  .user-info { display: none; }
}
@media (max-width: 600px) {
  h1 { font-size: 1.3rem; }
  .brand-text { display: none; }
  .form-grid { grid-template-columns: 1fr; }
  .span-2 { grid-column: auto; }
  .card { padding: 14px; }
  .page-header-actions, .group-select { width: 100%; }
  .page-header-actions .btn { flex: 1; }
  .owe-amount { margin-left: 0; }
  .toast-container { left: 12px; right: 12px; }
  .toast { max-width: none; }
}
##### FILE: src/main.jsx #####
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext.jsx";
import { ToastProvider } from "./context/ToastContext.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ToastProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>
);
##### FILE: src/pages/AddExpense.jsx #####
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import useUserGroups from "../hooks/useUserGroups";
import useSelectedGroup from "../hooks/useSelectedGroup";
import { addExpense, getGroup, getErrorMessage } from "../services/api";
import { formatCurrency, todayISO } from "../utils/format";
import PageHeader from "../components/PageHeader";
import GroupSelect from "../components/GroupSelect";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import NoGroups from "../components/NoGroups";

const SPLIT_TYPES = [
  { value: "equal", label: "Equal", hint: "Split equally among the selected members" },
  { value: "percentage", label: "Percentage", hint: "Enter a percentage for each member (total must be 100%)" },
  { value: "custom", label: "Custom amount", hint: "Enter an exact amount for each member (total must equal the expense)" },
];

export default function AddExpense() {
  const { user } = useAuth();
  const toast = useToast();
  const { groups, loading: groupsLoading, error: groupsError } = useUserGroups(user.id);
  const [groupId, selectGroup] = useSelectedGroup(groups);

  const [members, setMembers] = useState([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [form, setForm] = useState({ description: "", amount: "", date: todayISO(), paidBy: "", splitType: "equal" });
  const [selected, setSelected] = useState([]); // equal split participants
  const [percent, setPercent] = useState({});
  const [custom, setCustom] = useState({});
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  // Load the members of the selected group
  useEffect(() => {
    if (!groupId) return;
    let cancelled = false;
    setMembersLoading(true);
    setApiError("");
    getGroup(groupId)
      .then((res) => {
        if (cancelled) return;
        const list = res.data.members;
        setMembers(list);
        setSelected(list.map((m) => m.id));
        setPercent({});
        setCustom({});
        setForm((f) => ({ ...f, paidBy: list.some((m) => m.id === user.id) ? user.id : list[0]?.id ?? "" }));
      })
      .catch((err) => !cancelled && setApiError(getErrorMessage(err)))
      .finally(() => !cancelled && setMembersLoading(false));
    return () => { cancelled = true; };
  }, [groupId, user.id]);

  const sum = (obj) => members.reduce((total, m) => total + (Number(obj[m.id]) || 0), 0);
  const percentTotal = sum(percent);
  const customTotal = sum(custom);
  const amountNumber = Number(form.amount) || 0;
  const percentOk = Math.abs(percentTotal - 100) < 0.001;
  const customOk = amountNumber > 0 && Math.abs(customTotal - amountNumber) < 0.005;

  const toggleMember = (id) =>
    setSelected((list) => (list.includes(id) ? list.filter((x) => x !== id) : [...list, id]));

  const validate = () => {
    const found = {};
    if (!groupId) found.group = "Select a group";
    if (!form.description.trim()) found.description = "Description is required";
    if (form.amount === "" || isNaN(Number(form.amount))) found.amount = "Enter a valid amount";
    else if (Number(form.amount) <= 0) found.amount = "Amount must be greater than 0";
    if (!form.date) found.date = "Date is required";
    if (!form.paidBy) found.paidBy = "Select who paid";

    if (form.splitType === "equal" && selected.length === 0) found.split = "Select at least one member";
    if (form.splitType === "percentage") {
      const filled = members.filter((m) => percent[m.id] !== undefined && percent[m.id] !== "");
      if (filled.some((m) => isNaN(Number(percent[m.id])) || Number(percent[m.id]) < 0)) found.split = "Percentages must be valid positive numbers";
      else if (filled.length === 0) found.split = "Enter a percentage for at least one member";
      else if (!percentOk) found.split = `Percentages add up to ${percentTotal}%, but they must add up to 100%`;
    }
    if (form.splitType === "custom") {
      const filled = members.filter((m) => custom[m.id] !== undefined && custom[m.id] !== "");
      if (filled.some((m) => isNaN(Number(custom[m.id])) || Number(custom[m.id]) < 0)) found.split = "Amounts must be valid positive numbers";
      else if (filled.length === 0) found.split = "Enter an amount for at least one member";
      else if (!customOk) found.split = `Amounts add up to ${formatCurrency(customTotal)}, but the expense is ${formatCurrency(amountNumber)}`;
    }
    return found;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setApiError("");
    const found = validate();
    setErrors(found);
    if (Object.keys(found).length) return;

    // Build the exact request body the backend expects
    const payload = {
      group_id: Number(groupId),
      description: form.description.trim(),
      amount: Number(form.amount),
      paid_by: Number(form.paidBy),
      date: form.date,
      split_type: form.splitType,
    };
    if (form.splitType === "equal") payload.participants = selected;
    if (form.splitType === "percentage") {
      payload.splits = members
        .filter((m) => percent[m.id] !== undefined && percent[m.id] !== "")
        .map((m) => ({ user_id: m.id, percentage: Number(percent[m.id]) }));
    }
    if (form.splitType === "custom") {
      payload.splits = members
        .filter((m) => custom[m.id] !== undefined && custom[m.id] !== "")
        .map((m) => ({ user_id: m.id, amount: Number(custom[m.id]) }));
    }

    setSubmitting(true);
    try {
      const response = await addExpense(payload);
      toast(response.message);
      setResult(response.data); // the split calculated by the backend
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setResult(null);
    setErrors({});
    setForm((f) => ({ ...f, description: "", amount: "", date: todayISO() }));
    setPercent({});
    setCustom({});
    setSelected(members.map((m) => m.id));
  };

  if (groupsLoading) return <Loader text="Loading groups..." />;
  if (groupsError) return <ErrorBanner message={groupsError} />;
  if (groups.length === 0) return <NoGroups />;

  // ---------- Success screen: shows the split returned by the backend ----------
  if (result) {
    const nameOf = (id) => members.find((m) => m.id === id)?.name ?? `User ${id}`;
    return (
      <>
        <PageHeader title="Expense added ✔" subtitle="This is how the backend split the expense" />
        <section className="card">
          <h2 className="card-title">{result.description} — {formatCurrency(result.amount)}</h2>
          <p className="muted">Paid by <strong>{nameOf(result.paid_by)}</strong> · Split type: <strong>{result.split_type}</strong></p>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Member</th><th className="num">Share</th></tr></thead>
              <tbody>
                {result.shares.map((s) => (
                  <tr key={s.user_id}><td>{nameOf(s.user_id)}</td><td className="num">{formatCurrency(s.share_amount)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="row-actions">
            <button className="btn btn-primary" onClick={resetForm}>Add another expense</button>
            <Link className="btn btn-outline" to={`/expenses?group=${groupId}`}>View expenses</Link>
            <Link className="btn btn-outline" to={`/balances?group=${groupId}`}>View balances</Link>
          </div>
        </section>
      </>
    );
  }

  const splitInfo = SPLIT_TYPES.find((s) => s.value === form.splitType);

  return (
    <>
      <PageHeader title="Add Expense" subtitle="Record an expense and choose how to split it">
        <GroupSelect groups={groups} value={groupId} onChange={selectGroup} />
      </PageHeader>

      <ErrorBanner message={apiError} />
      {membersLoading ? (
        <Loader text="Loading members..." />
      ) : (
        <form className="card form-card" onSubmit={handleSubmit} noValidate>
          <div className="form-grid">
            <div className="field span-2">
              <label htmlFor="description">Description</label>
              <input id="description" placeholder="e.g. Hotel booking" value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })} />
              {errors.description && <span className="field-error">{errors.description}</span>}
            </div>
            <div className="field">
              <label htmlFor="amount">Amount (₹)</label>
              <input id="amount" type="number" step="0.01" min="0" placeholder="0.00" value={form.amount}
                onChange={(e) => setForm({ ...form, amount: e.target.value })} />
              {errors.amount && <span className="field-error">{errors.amount}</span>}
            </div>
            <div className="field">
              <label htmlFor="date">Date</label>
              <input id="date" type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
              {errors.date && <span className="field-error">{errors.date}</span>}
            </div>
            <div className="field span-2">
              <label htmlFor="paidBy">Paid by</label>
              <select id="paidBy" value={form.paidBy} onChange={(e) => setForm({ ...form, paidBy: Number(e.target.value) })}>
                {members.map((m) => <option key={m.id} value={m.id}>{m.name}{m.id === user.id ? " (You)" : ""}</option>)}
              </select>
              {errors.paidBy && <span className="field-error">{errors.paidBy}</span>}
            </div>
          </div>

          <h3 className="section-title">Split method</h3>
          <div className="tabs">
            {SPLIT_TYPES.map((s) => (
              <button type="button" key={s.value}
                className={`tab ${form.splitType === s.value ? "active" : ""}`}
                onClick={() => { setForm({ ...form, splitType: s.value }); setErrors({}); }}>
                {s.label}
              </button>
            ))}
          </div>
          <p className="muted small">{splitInfo.hint}</p>

          <div className="split-list">
            {members.map((m) => (
              <div className="split-row" key={m.id}>
                {form.splitType === "equal" ? (
                  <label className="check">
                    <input type="checkbox" checked={selected.includes(m.id)} onChange={() => toggleMember(m.id)} />
                    <span>{m.name}{m.id === user.id ? " (You)" : ""}</span>
                  </label>
                ) : (
                  <>
                    <span>{m.name}{m.id === user.id ? " (You)" : ""}</span>
                    <div className="input-suffix">
                      <input type="number" step="0.01" min="0"
                        placeholder={form.splitType === "percentage" ? "0" : "0.00"}
                        value={(form.splitType === "percentage" ? percent : custom)[m.id] ?? ""}
                        onChange={(e) =>
                          (form.splitType === "percentage" ? setPercent : setCustom)((p) => ({ ...p, [m.id]: e.target.value }))
                        } />
                      <em>{form.splitType === "percentage" ? "%" : "₹"}</em>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>

          {form.splitType === "percentage" && (
            <div className={`total-chip ${percentOk ? "ok" : "bad"}`}>Total: {percentTotal}% / 100%</div>
          )}
          {form.splitType === "custom" && (
            <div className={`total-chip ${customOk ? "ok" : "bad"}`}>
              Total: {formatCurrency(customTotal)} / {formatCurrency(amountNumber)}
            </div>
          )}
          {errors.split && <div className="field-error block">{errors.split}</div>}

          <div className="row-actions">
            <button className="btn btn-primary" disabled={submitting}>
              {submitting && <span className="spinner sm" />} {submitting ? "Saving..." : "Add Expense"}
            </button>
          </div>
        </form>
      )}
    </>
  );
}
##### FILE: src/pages/Balances.jsx #####
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import useUserGroups from "../hooks/useUserGroups";
import useSelectedGroup from "../hooks/useSelectedGroup";
import { getBalances, getErrorMessage } from "../services/api";
import { formatCurrency } from "../utils/format";
import PageHeader from "../components/PageHeader";
import GroupSelect from "../components/GroupSelect";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import NoGroups from "../components/NoGroups";
import StatCard from "../components/StatCard";
import StatusBadge from "../components/StatusBadge";

export default function Balances() {
  const { user } = useAuth();
  const { groups, loading: groupsLoading, error: groupsError } = useUserGroups(user.id);
  const [groupId, selectGroup] = useSelectedGroup(groups);

  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError("");
    try {
      setBalances((await getBalances(groupId)).data.balances);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    load();
  }, [load]);

  if (groupsLoading) return <Loader text="Loading groups..." />;
  if (groupsError) return <ErrorBanner message={groupsError} />;
  if (groups.length === 0) return <NoGroups />;

  const me = balances.find((b) => b.user_id === user.id);

  return (
    <>
      <PageHeader title="Balances" subtitle="Who paid, who owes, and the net position of every member">
        <GroupSelect groups={groups} value={groupId} onChange={selectGroup} />
        <Link to={`/settlements?group=${groupId}`} className="btn btn-primary">Go to Settlement</Link>
      </PageHeader>

      <ErrorBanner message={error} onRetry={load} />
      {loading ? (
        <Loader text="Calculating balances..." />
      ) : (
        !error && (
          <>
            {me && (
              <div className="grid-cards">
                <StatCard icon="📤" label="You paid" value={formatCurrency(me.total_paid)} tone="green" />
                <StatCard icon="📥" label="Your share (owed)" value={formatCurrency(me.total_owed)} tone="amber" />
                <StatCard icon="⚖️" label="Your net balance" value={formatCurrency(me.net_balance)}
                  tone={me.net_balance < 0 ? "red" : "green"}
                  hint={me.net_balance > 0 ? "You will receive" : me.net_balance < 0 ? "You need to pay" : "All settled"} />
              </div>
            )}

            <section className="card">
              <h2 className="card-title">Member balances</h2>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Member</th><th className="num">Total paid</th><th className="num">Total owed</th>
                      <th className="num">Net balance</th><th className="num">To receive</th><th className="num">To pay</th><th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {balances.map((b) => (
                      <tr key={b.user_id} className={b.user_id === user.id ? "me-row" : ""}>
                        <td>{b.name} {b.user_id === user.id && <span className="badge badge-gray">You</span>}</td>
                        <td className="num">{formatCurrency(b.total_paid)}</td>
                        <td className="num">{formatCurrency(b.total_owed)}</td>
                        <td className={`num ${b.net_balance > 0 ? "text-green" : b.net_balance < 0 ? "text-red" : ""}`}>{formatCurrency(b.net_balance)}</td>
                        <td className="num">{b.net_balance > 0 ? formatCurrency(b.net_balance) : "—"}</td>
                        <td className="num">{b.net_balance < 0 ? formatCurrency(-b.net_balance) : "—"}</td>
                        <td><StatusBadge status={b.status} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="muted small">Net balance = total paid − total owed (settlements already marked completed are taken into account by the backend).</p>
            </section>
          </>
        )
      )}
    </>
  );
}
##### FILE: src/pages/Dashboard.jsx #####
import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import useAllGroupData from "../hooks/useAllGroupData";
import { formatCurrency, formatDate } from "../utils/format";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import StatusBadge from "../components/StatusBadge";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";

export default function Dashboard() {
  const { user } = useAuth();
  const { loading, error, items, reload } = useAllGroupData(user.id);

  // Everything below is read from backend responses (only added up for display)
  const summary = useMemo(() => {
    let expenseCount = 0, totalAmount = 0, paid = 0, owed = 0, net = 0;
    const recentExpenses = [];
    const recentSettlements = [];
    const perGroup = [];

    items.forEach(({ group, expenses, totalSpent, balances, settlements }) => {
      expenseCount += expenses.length;
      totalAmount += totalSpent;
      const me = balances.find((b) => b.user_id === user.id);
      if (me) {
        paid += me.total_paid;
        owed += me.total_owed;
        net += me.net_balance;
      }
      perGroup.push({ group, totalSpent, expenseCount: expenses.length, myNet: me ? me.net_balance : 0 });
      expenses.forEach((e) => recentExpenses.push({ ...e, group_name: group.group_name }));
      settlements.forEach((s) => recentSettlements.push({ ...s, group_name: group.group_name }));
    });

    recentExpenses.sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
    recentSettlements.sort((a, b) => b.id - a.id);
    return {
      groups: items.length, expenseCount, totalAmount, paid, owed, net,
      recentExpenses: recentExpenses.slice(0, 5),
      recentSettlements: recentSettlements.slice(0, 5),
      perGroup,
    };
  }, [items, user.id]);

  if (loading) return <Loader text="Loading your dashboard..." />;

  return (
    <>
      <PageHeader title={`Hello, ${user.name} 👋`} subtitle="Here is the summary of all your groups">
        <Link to="/groups" className="btn btn-outline">Create Group</Link>
        <Link to="/expenses/new" className="btn btn-primary">Add Expense</Link>
      </PageHeader>

      <ErrorBanner message={error} onRetry={reload} />

      {!error && summary.groups === 0 ? (
        <EmptyState icon="🚀" title="Welcome! Let's get started" text="Create your first group to start adding expenses.">
          <Link to="/groups" className="btn btn-primary">Create Group</Link>
        </EmptyState>
      ) : (
        !error && (
          <>
            <div className="grid-cards">
              <StatCard icon="👥" label="Total Groups" value={summary.groups} />
              <StatCard icon="🧾" label="Total Expenses" value={summary.expenseCount} tone="blue" />
              <StatCard icon="💰" label="Total Amount" value={formatCurrency(summary.totalAmount)} tone="purple" hint="All expenses in your groups" />
              <StatCard icon="📤" label="You Paid" value={formatCurrency(summary.paid)} tone="green" />
              <StatCard icon="📥" label="You Owe (your share)" value={formatCurrency(summary.owed)} tone="amber" />
              <StatCard
                icon="⚖️"
                label="Net Balance"
                value={formatCurrency(summary.net)}
                tone={summary.net < 0 ? "red" : "green"}
                hint={summary.net > 0 ? "You get back" : summary.net < 0 ? "You owe" : "All settled"}
              />
            </div>

            <h2 className="section-title">Quick actions</h2>
            <div className="quick-actions">
              <Link to="/groups" className="quick-action"><span>👥</span>Create Group</Link>
              <Link to="/expenses/new" className="quick-action"><span>➕</span>Add Expense</Link>
              <Link to="/balances" className="quick-action"><span>⚖️</span>View Balance</Link>
              <Link to="/settlements" className="quick-action"><span>🤝</span>Settlement</Link>
              <Link to="/history" className="quick-action"><span>📈</span>History</Link>
            </div>

            <div className="two-col">
              <section className="card">
                <h2 className="card-title">Recent expenses</h2>
                {summary.recentExpenses.length === 0 ? (
                  <p className="muted">No expenses added yet.</p>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>Description</th><th>Group</th><th>Paid by</th><th>Date</th><th className="num">Amount</th></tr></thead>
                      <tbody>
                        {summary.recentExpenses.map((e) => (
                          <tr key={e.id}>
                            <td>{e.description}</td><td>{e.group_name}</td><td>{e.paid_by_name}</td>
                            <td>{formatDate(e.date)}</td><td className="num">{formatCurrency(e.amount)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>

              <section className="card">
                <h2 className="card-title">Recent settlements</h2>
                {summary.recentSettlements.length === 0 ? (
                  <p className="muted">No settlements generated yet.</p>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead><tr><th>From → To</th><th>Group</th><th className="num">Amount</th><th>Status</th></tr></thead>
                      <tbody>
                        {summary.recentSettlements.map((s) => (
                          <tr key={s.id}>
                            <td>{s.from_name} → {s.to_name}</td><td>{s.group_name}</td>
                            <td className="num">{formatCurrency(s.amount)}</td><td><StatusBadge status={s.status} /></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </div>

            <section className="card">
              <h2 className="card-title">Your groups</h2>
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Group</th><th className="num">Expenses</th><th className="num">Total spent</th><th className="num">Your net balance</th><th></th></tr></thead>
                  <tbody>
                    {summary.perGroup.map(({ group, totalSpent, expenseCount, myNet }) => (
                      <tr key={group.id}>
                        <td><Link to={`/groups/${group.id}`}>{group.group_name}</Link></td>
                        <td className="num">{expenseCount}</td>
                        <td className="num">{formatCurrency(totalSpent)}</td>
                        <td className={`num ${myNet > 0 ? "text-green" : myNet < 0 ? "text-red" : ""}`}>{formatCurrency(myNet)}</td>
                        <td><Link className="btn btn-sm btn-outline" to={`/balances?group=${group.id}`}>Balance</Link></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )
      )}
    </>
  );
}
##### FILE: src/pages/Expenses.jsx #####
import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import useUserGroups from "../hooks/useUserGroups";
import useSelectedGroup from "../hooks/useSelectedGroup";
import { getGroupExpenses, getErrorMessage } from "../services/api";
import { formatCurrency, formatDate } from "../utils/format";
import PageHeader from "../components/PageHeader";
import GroupSelect from "../components/GroupSelect";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import NoGroups from "../components/NoGroups";
import StatCard from "../components/StatCard";

export default function Expenses() {
  const { user } = useAuth();
  const { groups, loading: groupsLoading, error: groupsError } = useUserGroups(user.id);
  const [groupId, selectGroup] = useSelectedGroup(groups);

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [openId, setOpenId] = useState(null);

  const load = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError("");
    try {
      setData((await getGroupExpenses(groupId)).data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    return data.expenses.filter((e) => !q || e.description.toLowerCase().includes(q) || e.paid_by_name.toLowerCase().includes(q));
  }, [data, search]);

  if (groupsLoading) return <Loader text="Loading groups..." />;
  if (groupsError) return <ErrorBanner message={groupsError} />;
  if (groups.length === 0) return <NoGroups />;

  return (
    <>
      <PageHeader title="Expenses" subtitle="All expenses of a group and how each was split">
        <GroupSelect groups={groups} value={groupId} onChange={selectGroup} />
        <Link to={`/expenses/new?group=${groupId}`} className="btn btn-primary">+ Add Expense</Link>
      </PageHeader>

      <ErrorBanner message={error} onRetry={load} />
      {loading || !data ? (
        <Loader text="Loading expenses..." />
      ) : (
        <>
          <div className="grid-cards">
            <StatCard icon="🧾" label="Expenses" value={data.expenses.length} tone="blue" />
            <StatCard icon="💰" label="Total Spent" value={formatCurrency(data.total_spent)} tone="purple" />
          </div>
          <section className="card">
            <div className="toolbar">
              <input className="search" placeholder="Search description or payer..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            {filtered.length === 0 ? (
              <EmptyState icon="🧾" title={data.expenses.length ? "No matching expenses" : "No expenses yet"}
                text={data.expenses.length ? "Try a different search." : "Add the first expense for this group."} />
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>Date</th><th>Description</th><th>Paid by</th><th className="num">Amount</th><th></th></tr></thead>
                  <tbody>
                    {filtered.map((e) => (
                      <Fragment key={e.id}>
                        <tr>
                          <td>{formatDate(e.date)}</td><td>{e.description}</td><td>{e.paid_by_name}</td>
                          <td className="num">{formatCurrency(e.amount)}</td>
                          <td className="num">
                            <button className="btn btn-sm btn-outline" onClick={() => setOpenId(openId === e.id ? null : e.id)}>
                              {openId === e.id ? "Hide split" : "View split"}
                            </button>
                          </td>
                        </tr>
                        {openId === e.id && (
                          <tr className="detail-row">
                            <td colSpan={5}>
                              <div className="chips">
                                {e.splits.map((s) => (
                                  <span className="chip" key={s.user_id}>{s.name}: <strong>{formatCurrency(s.share_amount)}</strong></span>
                                ))}
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}
##### FILE: src/pages/GroupDetails.jsx #####
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { addGroupMember, getGroup, getGroupExpenses, getUsers, getErrorMessage } from "../services/api";
import { formatCurrency, formatDate, isValidEmail } from "../utils/format";
import PageHeader from "../components/PageHeader";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import StatCard from "../components/StatCard";

export default function GroupDetails() {
  const { groupId } = useParams();
  const { user } = useAuth();
  const toast = useToast();

  const [group, setGroup] = useState(null);
  const [expenseData, setExpenseData] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedUser, setSelectedUser] = useState("");
  const [email, setEmail] = useState("");
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [g, e, u] = await Promise.all([getGroup(groupId), getGroupExpenses(groupId), getUsers()]);
      setGroup(g.data);
      setExpenseData(e.data);
      setAllUsers(u.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAdd = async (event) => {
    event.preventDefault();
    setAddError("");
    let payload;
    if (selectedUser) payload = { user_id: Number(selectedUser) };
    else if (email.trim()) {
      if (!isValidEmail(email.trim())) return setAddError("Enter a valid email address");
      payload = { email: email.trim() };
    } else return setAddError("Choose a user from the list or type an email");

    setAdding(true);
    try {
      const response = await addGroupMember(groupId, payload);
      toast(response.message);
      setSelectedUser("");
      setEmail("");
      await load();
    } catch (err) {
      setAddError(getErrorMessage(err));
    } finally {
      setAdding(false);
    }
  };

  if (loading) return <Loader text="Loading group..." />;
  if (error) return <ErrorBanner message={error} onRetry={load} />;

  const memberIds = new Set(group.members.map((m) => m.id));
  const availableUsers = allUsers.filter((u) => !memberIds.has(u.id));

  return (
    <>
      <PageHeader title={group.group_name} subtitle={`Created by ${group.created_by_name}`}>
        <Link to="/groups" className="btn btn-outline">← All Groups</Link>
        <Link to={`/expenses/new?group=${group.id}`} className="btn btn-primary">Add Expense</Link>
      </PageHeader>

      <div className="grid-cards">
        <StatCard icon="👥" label="Members" value={group.member_count} />
        <StatCard icon="🧾" label="Expenses" value={expenseData.expenses.length} tone="blue" />
        <StatCard icon="💰" label="Total Spent" value={formatCurrency(expenseData.total_spent)} tone="purple" />
      </div>

      <div className="quick-actions">
        <Link to={`/expenses?group=${group.id}`} className="quick-action"><span>🧾</span>View Expenses</Link>
        <Link to={`/balances?group=${group.id}`} className="quick-action"><span>⚖️</span>Balances</Link>
        <Link to={`/settlements?group=${group.id}`} className="quick-action"><span>🤝</span>Settlements</Link>
      </div>

      <div className="two-col">
        <section className="card">
          <h2 className="card-title">Members ({group.member_count})</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead>
              <tbody>
                {group.members.map((m) => (
                  <tr key={m.id}>
                    <td>{m.name} {m.id === user.id && <span className="badge badge-gray">You</span>}</td>
                    <td>{m.email}</td>
                    <td>{m.id === group.created_by ? <span className="badge badge-blue">Creator</span> : "Member"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="card">
          <h2 className="card-title">Add member</h2>
          <ErrorBanner message={addError} />
          <form onSubmit={handleAdd} noValidate>
            <div className="field">
              <label htmlFor="member-select">Choose a registered user</label>
              <select id="member-select" value={selectedUser} onChange={(e) => { setSelectedUser(e.target.value); setEmail(""); }}>
                <option value="">— Select user —</option>
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>{u.name} ({u.email})</option>
                ))}
              </select>
            </div>
            <p className="muted small center">or</p>
            <div className="field">
              <label htmlFor="member-email">Add by email</label>
              <input id="member-email" type="email" placeholder="friend@example.com" value={email}
                onChange={(e) => { setEmail(e.target.value); setSelectedUser(""); }} />
            </div>
            <button className="btn btn-primary" disabled={adding}>
              {adding && <span className="spinner sm" />} Add Member
            </button>
          </form>
        </section>
      </div>

      <section className="card">
        <h2 className="card-title">Recent expenses</h2>
        {expenseData.expenses.length === 0 ? (
          <EmptyState icon="🧾" title="No expenses yet" text="Add the first expense for this group." />
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Date</th><th>Description</th><th>Paid by</th><th className="num">Amount</th></tr></thead>
              <tbody>
                {expenseData.expenses.slice(0, 5).map((e) => (
                  <tr key={e.id}>
                    <td>{formatDate(e.date)}</td><td>{e.description}</td><td>{e.paid_by_name}</td>
                    <td className="num">{formatCurrency(e.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
##### FILE: src/pages/Groups.jsx #####
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import useUserGroups from "../hooks/useUserGroups";
import { createGroup, getErrorMessage } from "../services/api";
import PageHeader from "../components/PageHeader";
import Modal from "../components/Modal";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";

export default function Groups() {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const { groups, loading, error, reload } = useUserGroups(user.id);

  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [apiError, setApiError] = useState("");
  const [saving, setSaving] = useState(false);

  const closeModal = () => {
    setModalOpen(false);
    setName("");
    setFieldError("");
    setApiError("");
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setApiError("");
    if (!name.trim()) {
      setFieldError("Group name is required");
      return;
    }
    setFieldError("");
    setSaving(true);
    try {
      const response = await createGroup({ group_name: name.trim(), created_by: user.id });
      toast(response.message);
      closeModal();
      navigate(`/groups/${response.data.id}`);
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader title="Groups" subtitle="Groups you created or were added to">
        <button className="btn btn-primary" onClick={() => setModalOpen(true)}>+ Create Group</button>
      </PageHeader>

      <ErrorBanner message={error} onRetry={reload} />
      {loading ? (
        <Loader text="Loading groups..." />
      ) : groups.length === 0 && !error ? (
        <EmptyState icon="👥" title="No groups yet" text="Create a group like “Goa Trip” or “Flat Expenses”.">
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>Create your first group</button>
        </EmptyState>
      ) : (
        <div className="grid-groups">
          {groups.map((group) => (
            <div className="card group-card" key={group.id}>
              <div className="group-avatar">{group.group_name.charAt(0).toUpperCase()}</div>
              <h3>{group.group_name}</h3>
              <p className="muted">{group.created_by === user.id ? "Created by you" : "You are a member"}</p>
              <div className="group-card-actions">
                <Link to={`/groups/${group.id}`} className="btn btn-sm btn-primary">View Details</Link>
                <Link to={`/expenses/new?group=${group.id}`} className="btn btn-sm btn-outline">Add Expense</Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} title="Create a new group" onClose={closeModal}>
        <form onSubmit={handleCreate} noValidate>
          <ErrorBanner message={apiError} />
          <div className="field">
            <label htmlFor="group_name">Group name</label>
            <input id="group_name" autoFocus placeholder="e.g. Goa Trip" value={name} onChange={(e) => setName(e.target.value)} />
            {fieldError && <span className="field-error">{fieldError}</span>}
          </div>
          <p className="muted small">You will be added to the group automatically.</p>
          <div className="modal-actions">
            <button type="button" className="btn btn-outline" onClick={closeModal} disabled={saving}>Cancel</button>
            <button className="btn btn-primary" disabled={saving}>
              {saving && <span className="spinner sm" />} Create Group
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
##### FILE: src/pages/History.jsx #####
import { useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";
import useAllGroupData from "../hooks/useAllGroupData";
import { downloadCsv, formatCurrency, formatDate } from "../utils/format";
import PageHeader from "../components/PageHeader";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import StatCard from "../components/StatCard";
import StatusBadge from "../components/StatusBadge";

export default function History() {
  const { user } = useAuth();
  const { loading, error, items, reload } = useAllGroupData(user.id);

  const [tab, setTab] = useState("expenses");
  const [search, setSearch] = useState("");
  const [groupFilter, setGroupFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");

  // Flatten backend data for easy filtering
  const { allExpenses, allSettlements } = useMemo(() => {
    const e = [], s = [];
    items.forEach(({ group, expenses, settlements }) => {
      expenses.forEach((x) => e.push({ ...x, group_name: group.group_name }));
      settlements.forEach((x) => s.push({ ...x, group_name: group.group_name }));
    });
    e.sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id);
    s.sort((a, b) => b.id - a.id);
    return { allExpenses: e, allSettlements: s };
  }, [items]);

  const q = search.trim().toLowerCase();
  const expenses = allExpenses.filter(
    (e) =>
      (groupFilter === "all" || e.group_id === Number(groupFilter)) &&
      (!q || e.description.toLowerCase().includes(q) || e.paid_by_name.toLowerCase().includes(q)) &&
      (!from || e.date >= from) && (!to || e.date <= to)
  );
  const settlements = allSettlements.filter(
    (s) =>
      (groupFilter === "all" || s.group_id === Number(groupFilter)) &&
      (statusFilter === "all" || s.status === statusFilter) &&
      (!q || s.from_name.toLowerCase().includes(q) || s.to_name.toLowerCase().includes(q))
  );

  const sum = (list, key = "amount") => list.reduce((t, x) => t + x[key], 0);
  const totalExpenseAmount = sum(allExpenses);
  const pendingAmount = sum(allSettlements.filter((s) => s.status === "pending"));
  const completedAmount = sum(allSettlements.filter((s) => s.status === "completed"));
  const maxSpent = Math.max(1, ...items.map((i) => i.totalSpent));

  const exportCsv = () =>
    downloadCsv("expense-history.csv", ["Date", "Group", "Description", "Paid by", "Amount", "Split"],
      expenses.map((e) => [e.date, e.group_name, e.description, e.paid_by_name, e.amount,
        e.splits.map((s) => `${s.name}: ${s.share_amount}`).join("; ")]));

  const clearFilters = () => { setSearch(""); setGroupFilter("all"); setStatusFilter("all"); setFrom(""); setTo(""); };

  if (loading) return <Loader text="Loading history..." />;

  return (
    <>
      <PageHeader title="History & Reports" subtitle="Complete record of expenses and settlements across your groups">
        {tab === "expenses" && expenses.length > 0 && <button className="btn btn-outline" onClick={exportCsv}>⬇ Export CSV</button>}
      </PageHeader>
      <ErrorBanner message={error} onRetry={reload} />

      {!error && (
        <>
          <div className="grid-cards">
            <StatCard icon="🧾" label="Total Expenses" value={allExpenses.length} tone="blue" />
            <StatCard icon="💰" label="Total Amount" value={formatCurrency(totalExpenseAmount)} tone="purple" />
            <StatCard icon="⏳" label="Pending Settlements" value={formatCurrency(pendingAmount)} tone="amber" />
            <StatCard icon="✅" label="Completed Settlements" value={formatCurrency(completedAmount)} tone="green" />
          </div>

          <div className="tabs">
            <button className={`tab ${tab === "expenses" ? "active" : ""}`} onClick={() => setTab("expenses")}>Expense History</button>
            <button className={`tab ${tab === "settlements" ? "active" : ""}`} onClick={() => setTab("settlements")}>Settlement History</button>
            <button className={`tab ${tab === "groups" ? "active" : ""}`} onClick={() => setTab("groups")}>Group-wise Report</button>
          </div>

          {tab !== "groups" && (
            <div className="toolbar card">
              <input className="search" placeholder={tab === "expenses" ? "Search description or payer..." : "Search by member name..."}
                value={search} onChange={(e) => setSearch(e.target.value)} />
              <select value={groupFilter} onChange={(e) => setGroupFilter(e.target.value)}>
                <option value="all">All groups</option>
                {items.map(({ group }) => <option key={group.id} value={group.id}>{group.group_name}</option>)}
              </select>
              {tab === "expenses" ? (
                <>
                  <label className="inline-field">From <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
                  <label className="inline-field">To <input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
                </>
              ) : (
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                  <option value="all">All status</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
              )}
              <button className="btn btn-sm btn-outline" onClick={clearFilters}>Clear</button>
            </div>
          )}

          {tab === "expenses" && (
            <section className="card">
              <h2 className="card-title">Expense history ({expenses.length}) · {formatCurrency(sum(expenses))}</h2>
              {expenses.length === 0 ? (
                <EmptyState icon="🔎" title="No expenses found" text="Change the filters or add an expense." />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Date</th><th>Group</th><th>Description</th><th>Paid by</th><th>Split</th><th className="num">Amount</th></tr></thead>
                    <tbody>
                      {expenses.map((e) => (
                        <tr key={e.id}>
                          <td>{formatDate(e.date)}</td><td>{e.group_name}</td><td>{e.description}</td><td>{e.paid_by_name}</td>
                          <td className="small muted">{e.splits.map((s) => `${s.name} ${formatCurrency(s.share_amount)}`).join(" · ")}</td>
                          <td className="num">{formatCurrency(e.amount)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {tab === "settlements" && (
            <section className="card">
              <h2 className="card-title">Settlement history ({settlements.length})</h2>
              {settlements.length === 0 ? (
                <EmptyState icon="🤝" title="No settlements found" text="Generate settlements from the Settlement page." />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>#</th><th>Group</th><th>From</th><th>To</th><th className="num">Amount</th><th>Status</th></tr></thead>
                    <tbody>
                      {settlements.map((s) => (
                        <tr key={s.id}>
                          <td>{s.id}</td><td>{s.group_name}</td><td>{s.from_name}</td><td>{s.to_name}</td>
                          <td className="num">{formatCurrency(s.amount)}</td><td><StatusBadge status={s.status} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {tab === "groups" && (
            <section className="card">
              <h2 className="card-title">Group-wise expenses & financial summary</h2>
              {items.length === 0 ? (
                <EmptyState icon="👥" title="No groups yet" />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Group</th><th className="num">Expenses</th><th>Total spent</th><th className="num">Pending</th><th className="num">Completed</th></tr></thead>
                    <tbody>
                      {items.map(({ group, expenses: ex, totalSpent, settlements: st }) => (
                        <tr key={group.id}>
                          <td>{group.group_name}</td>
                          <td className="num">{ex.length}</td>
                          <td>
                            <div className="bar-cell">
                              <div className="bar"><div style={{ width: `${(totalSpent / maxSpent) * 100}%` }} /></div>
                              <span>{formatCurrency(totalSpent)}</span>
                            </div>
                          </td>
                          <td className="num">{formatCurrency(sum(st.filter((s) => s.status === "pending")))}</td>
                          <td className="num">{formatCurrency(sum(st.filter((s) => s.status === "completed")))}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr><td>Total</td><td className="num">{allExpenses.length}</td><td>{formatCurrency(totalExpenseAmount)}</td>
                        <td className="num">{formatCurrency(pendingAmount)}</td><td className="num">{formatCurrency(completedAmount)}</td></tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </section>
          )}
        </>
      )}
    </>
  );
}
##### FILE: src/pages/Login.jsx #####
import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getErrorMessage } from "../services/api";
import { isValidEmail } from "../utils/format";
import ErrorBanner from "../components/ErrorBanner";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  const validate = () => {
    const found = {};
    if (!form.email.trim()) found.email = "Email is required";
    else if (!isValidEmail(form.email.trim())) found.email = "Enter a valid email address";
    if (!form.password) found.password = "Password is required";
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
      await login(form.email.trim(), form.password);
      navigate(location.state?.from || "/dashboard", { replace: true });
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
        <h1>Welcome back</h1>
        <p className="muted">Login to manage your shared expenses</p>

        {location.state?.registered && (
          <ErrorBanner type="success" message="Registration successful! Please login." />
        )}
        <ErrorBanner message={apiError} />

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            {errors.email && <span className="field-error">{errors.email}</span>}
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Your password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            {errors.password && <span className="field-error">{errors.password}</span>}
          </div>
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading && <span className="spinner sm" />} {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <p className="auth-switch">
          New here? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
##### FILE: src/pages/NotFound.jsx #####
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
##### FILE: src/pages/Register.jsx #####
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
##### FILE: src/pages/Settlements.jsx #####
import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import useUserGroups from "../hooks/useUserGroups";
import useSelectedGroup from "../hooks/useSelectedGroup";
import {
  generateSettlements, getGroupSettlements, getSuggestedPayments,
  updateSettlementStatus, getErrorMessage,
} from "../services/api";
import { formatCurrency } from "../utils/format";
import PageHeader from "../components/PageHeader";
import GroupSelect from "../components/GroupSelect";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import NoGroups from "../components/NoGroups";
import StatusBadge from "../components/StatusBadge";
import StatCard from "../components/StatCard";
import ConfirmDialog from "../components/ConfirmDialog";

export default function Settlements() {
  const { user } = useAuth();
  const toast = useToast();
  const { groups, loading: groupsLoading, error: groupsError } = useUserGroups(user.id);
  const [groupId, selectGroup] = useSelectedGroup(groups);

  const [payments, setPayments] = useState([]);   // who owes whom (calculated by backend)
  const [saved, setSaved] = useState([]);         // settlements stored in the database
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const [confirmGenerate, setConfirmGenerate] = useState(false);
  const [statusChange, setStatusChange] = useState(null); // { settlement, status }
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError("");
    try {
      const [suggest, list] = await Promise.all([getSuggestedPayments(groupId), getGroupSettlements(groupId)]);
      setPayments(suggest.data.payments);
      setSaved(list.data.settlements);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleGenerate = async () => {
    setBusy(true);
    try {
      const response = await generateSettlements(groupId);
      toast(response.message);
      setConfirmGenerate(false);
      await load();
    } catch (err) {
      setConfirmGenerate(false);
      toast(getErrorMessage(err), "error");
    } finally {
      setBusy(false);
    }
  };

  const handleStatus = async () => {
    setBusy(true);
    try {
      const response = await updateSettlementStatus(statusChange.settlement.id, statusChange.status);
      toast(response.message);
      setStatusChange(null);
      await load();
    } catch (err) {
      setStatusChange(null);
      toast(getErrorMessage(err), "error");
    } finally {
      setBusy(false);
    }
  };

  if (groupsLoading) return <Loader text="Loading groups..." />;
  if (groupsError) return <ErrorBanner message={groupsError} />;
  if (groups.length === 0) return <NoGroups />;

  const pending = saved.filter((s) => s.status === "pending");
  const completed = saved.filter((s) => s.status === "completed");
  const sumOf = (list) => list.reduce((t, s) => t + s.amount, 0);
  const visible = filter === "all" ? saved : saved.filter((s) => s.status === filter);

  return (
    <>
      <PageHeader title="Settlements" subtitle="See who owes whom and track the payments">
        <GroupSelect groups={groups} value={groupId} onChange={selectGroup} />
      </PageHeader>

      <ErrorBanner message={error} onRetry={load} />
      {loading ? (
        <Loader text="Calculating settlements..." />
      ) : (
        !error && (
          <>
            <div className="grid-cards">
              <StatCard icon="⏳" label="Pending" value={`${pending.length} · ${formatCurrency(sumOf(pending))}`} tone="amber" />
              <StatCard icon="✅" label="Completed" value={`${completed.length} · ${formatCurrency(sumOf(completed))}`} tone="green" />
            </div>

            <section className="card">
              <div className="card-head">
                <h2 className="card-title">Who owes whom</h2>
                <button className="btn btn-primary" disabled={payments.length === 0} onClick={() => setConfirmGenerate(true)}>
                  Save as pending settlements
                </button>
              </div>
              {payments.length === 0 ? (
                <EmptyState icon="🎉" title="All settled!" text="Nobody owes anything in this group right now." />
              ) : (
                <ul className="owe-list">
                  {payments.map((p, index) => (
                    <li key={index}>
                      <span className="owe-from">{p.from_name}</span>
                      <span className="owe-arrow">owes →</span>
                      <span className="owe-to">{p.to_name}</span>
                      <strong className="owe-amount">{formatCurrency(p.amount)}</strong>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="card">
              <div className="card-head">
                <h2 className="card-title">Settlement status</h2>
                <div className="tabs compact">
                  {["all", "pending", "completed"].map((f) => (
                    <button key={f} className={`tab ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                      {f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              {visible.length === 0 ? (
                <EmptyState icon="🤝" title="No settlements to show"
                  text={saved.length === 0 ? "Click “Save as pending settlements” above to create them." : "Nothing in this filter."} />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>#</th><th>From</th><th>To</th><th className="num">Amount</th><th>Status</th><th></th></tr></thead>
                    <tbody>
                      {visible.map((s) => (
                        <tr key={s.id}>
                          <td>{s.id}</td><td>{s.from_name}</td><td>{s.to_name}</td>
                          <td className="num">{formatCurrency(s.amount)}</td>
                          <td><StatusBadge status={s.status} /></td>
                          <td className="num">
                            {s.status === "pending" ? (
                              <button className="btn btn-sm btn-success" onClick={() => setStatusChange({ settlement: s, status: "completed" })}>Mark completed</button>
                            ) : (
                              <button className="btn btn-sm btn-outline" onClick={() => setStatusChange({ settlement: s, status: "pending" })}>Mark pending</button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )
      )}

      <ConfirmDialog
        open={confirmGenerate}
        title="Save settlements"
        message="This saves the “who owes whom” list as pending settlements. Any existing pending settlements of this group will be replaced (completed ones are kept)."
        confirmText="Save settlements"
        loading={busy}
        onConfirm={handleGenerate}
        onCancel={() => setConfirmGenerate(false)}
      />
      <ConfirmDialog
        open={Boolean(statusChange)}
        title={`Mark as ${statusChange?.status}`}
        message={statusChange ? `${statusChange.settlement.from_name} → ${statusChange.settlement.to_name}, ${formatCurrency(statusChange.settlement.amount)}: mark this settlement as ${statusChange.status}?` : ""}
        confirmText="Yes, update"
        loading={busy}
        onConfirm={handleStatus}
        onCancel={() => setStatusChange(null)}
      />
    </>
  );
}
##### FILE: src/services/api.js #####
/**
 * api.js - Centralised Axios service for the Flask backend.
 *
 * BACKEND URL: change it in ".env" (VITE_API_BASE_URL) - nowhere else.
 *
 * Every backend response has this shape:
 *   success: { success: true,  message: "...", data: ... }
 *   error:   { success: false, message: "..." }
 * Each function below returns that body, so callers use `res.data` and `res.message`.
 *
 * The backend has NO token / JWT / session. Login simply returns the user object.
 */
import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** Turn any Axios error into a short, friendly sentence. */
export function getErrorMessage(error) {
  if (error?.response) {
    const { data, status } = error.response;
    if (data && typeof data.message === "string") return data.message; // message written by the Flask backend
    return `Server returned an error (status ${status}).`;
  }
  if (error?.code === "ECONNABORTED") return "The server took too long to respond. Please try again.";
  if (error?.request) {
    return `Cannot reach the backend at ${API_BASE_URL}. Please make sure the Flask server is running.`;
  }
  return error?.message || "Something went wrong.";
}

const send = (request) => request.then((response) => response.data);

// ---------------- AUTH  (routes/auth_routes.py) ----------------
export const registerUser = ({ name, email, password }) =>
  send(client.post("/api/auth/register", { name, email, password }));

export const loginUser = ({ email, password }) =>
  send(client.post("/api/auth/login", { email, password }));

export const getUsers = () => send(client.get("/api/auth/users"));
export const getUser = (userId) => send(client.get(`/api/auth/users/${userId}`));

// ---------------- GROUPS  (routes/group_routes.py) ----------------
export const createGroup = ({ group_name, created_by }) =>
  send(client.post("/api/groups", { group_name, created_by }));

export const getUserGroups = (userId) => send(client.get(`/api/groups/user/${userId}`));
export const getGroup = (groupId) => send(client.get(`/api/groups/${groupId}`));

/** payload is { user_id } OR { email } */
export const addGroupMember = (groupId, payload) =>
  send(client.post(`/api/groups/${groupId}/members`, payload));

// ---------------- EXPENSES  (routes/expense_routes.py) ----------------
/**
 * payload: {
 *   group_id, description, amount, paid_by, date?, split_type: "equal"|"percentage"|"custom",
 *   participants?: [ids]                         (equal)
 *   splits?: [{user_id, percentage}|{user_id, amount}]   (percentage / custom)
 * }
 */
export const addExpense = (payload) => send(client.post("/api/expenses", payload));
export const getGroupExpenses = (groupId) => send(client.get(`/api/expenses/group/${groupId}`));
export const getExpense = (expenseId) => send(client.get(`/api/expenses/${expenseId}`));

// ---------------- BALANCES & SETTLEMENTS  (routes/settlement_routes.py) ----------------
export const getBalances = (groupId) => send(client.get(`/api/settlements/balances/${groupId}`));
export const getSuggestedPayments = (groupId) => send(client.get(`/api/settlements/suggest/${groupId}`));
export const generateSettlements = (groupId) => send(client.post(`/api/settlements/generate/${groupId}`));
export const getGroupSettlements = (groupId) => send(client.get(`/api/settlements/group/${groupId}`));
export const updateSettlementStatus = (settlementId, status) =>
  send(client.put(`/api/settlements/${settlementId}/status`, { status }));

export default client;
##### FILE: src/utils/format.js #####
const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
});

export const formatCurrency = (value) => currencyFormatter.format(Number(value) || 0);

/** "2025-01-20" -> "20 Jan 2025" */
export function formatDate(value) {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  if (isNaN(date)) return value;
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

/** Today's date as YYYY-MM-DD in the user's local time (format the backend expects). */
export function todayISO() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

export const isValidEmail = (email) => /^[\w.\-+]+@[\w-]+\.[\w.-]+$/.test(email);

/** Build and download a CSV file in the browser. rows = array of arrays. */
export function downloadCsv(filename, headers, rows) {
  const escape = (cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map((row) => row.map(escape).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
'''

def main():
    if os.path.exists(TARGET):
        print(f'Folder "{TARGET}" already exists. Rename or delete it first, then run again.')
        sys.exit(1)
    count = 0
    parts = BUNDLE.split("##### FILE: ")[1:]
    for part in parts:
        path, _, content = part.partition(" #####\n")
        full = os.path.join(TARGET, *path.split("/"))
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        count += 1
    print(f"Done! {count} files created inside the '{TARGET}' folder.")
    print("Next:  cd frontend  ->  npm install  ->  npm run dev")

if __name__ == "__main__":
    main()
