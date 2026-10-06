# Expense Split and Settlement System – Backend

Flask + MySQL REST API (B.Tech project).

## Folder structure
```
backend/
├── app.py                  # starts the server, registers routes, error handlers
├── config.py               # database settings
├── database.py             # MySQL connection + helper functions
├── models.py               # all SQL queries
├── schema.sql              # database creation script
├── requirements.txt
├── Expense_Split_API.postman_collection.json
├── routes/
│   ├── auth_routes.py      # register / login
│   ├── group_routes.py     # groups and members
│   ├── expense_routes.py   # add expense, history, split
│   └── settlement_routes.py# balances, who owes whom, settlement status
└── utils/
    ├── split_algorithm.py  # equal / percentage / custom split + balance logic
    └── helpers.py          # common JSON response format
```

## Installation
1. Install Python 3.9+ and MySQL Server 8.
2. Create the database:
   ```
   mysql -u root -p < schema.sql
   ```
3. Open `config.py` and set `DB_PASSWORD` to your MySQL password.
4. Create a virtual environment and install packages:
   ```
   cd backend
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate       (Mac / Linux)
   pip install -r requirements.txt
   ```

## Run
```
python app.py
```
Server: http://127.0.0.1:5000 — check DB connection at http://127.0.0.1:5000/api/health

## Test with Postman
Import `Expense_Split_API.postman_collection.json` and run the folders in order (1 → 4).
The collection assumes fresh tables, so ids start from 1.

## API list
| Method | URL | Purpose |
|---|---|---|
| POST | /api/auth/register | Register user |
| POST | /api/auth/login | Login |
| GET | /api/auth/users | List users |
| POST | /api/groups | Create group (creator auto-added) |
| GET | /api/groups/user/{user_id} | Groups of a user |
| GET | /api/groups/{id} | Group details + members |
| POST | /api/groups/{id}/members | Add member (`user_id` or `email`) |
| POST | /api/expenses | Add expense with equal / percentage / custom split |
| GET | /api/expenses/group/{group_id} | Expense history |
| GET | /api/expenses/{id} | One expense with split |
| GET | /api/settlements/balances/{group_id} | Paid, owed, net balance |
| GET | /api/settlements/suggest/{group_id} | Who owes whom (preview) |
| POST | /api/settlements/generate/{group_id} | Save settlements as pending |
| GET | /api/settlements/group/{group_id} | List settlements |
| PUT | /api/settlements/{id}/status | Set `pending` / `completed` |

## Expense request examples
Equal (leave out `participants` to include everyone):
```json
{"group_id":1,"description":"Hotel","amount":3000,"paid_by":1,"split_type":"equal"}
```
Percentage:
```json
{"group_id":1,"description":"Dinner","amount":1000,"paid_by":3,"split_type":"percentage",
 "splits":[{"user_id":1,"percentage":50},{"user_id":2,"percentage":30},{"user_id":3,"percentage":20}]}
```
Custom:
```json
{"group_id":1,"description":"Shopping","amount":900,"paid_by":1,"split_type":"custom",
 "splits":[{"user_id":1,"amount":500},{"user_id":2,"amount":300},{"user_id":3,"amount":100}]}
```

## How the balance logic works
- `net = total_paid − total_owed − received + sent` (sent/received = completed settlements)
- Positive net → the person gets money back; negative → the person owes money.
- `simplify_debts` matches the biggest debtor with the biggest creditor to minimise the number of payments.
- Money uses Python `Decimal` (not float) to avoid rounding errors.

## Extra items beyond the required tables
- `expense_splits` table – stores each person's share of each expense (required for the 3 split types).
- `settlements.group_id` – so settlements belong to a group.
