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
