"""
models.py - All database queries, grouped by table.
Routes call these functions, so SQL lives in one place only.
"""
from database import fetch_all, fetch_one, execute_query, get_connection


# ==================================================================
# USERS
# ==================================================================
def create_user(name, email, hashed_password):
    return execute_query(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (name, email, hashed_password),
    )


def get_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email = %s", (email,))


def get_user_by_id(user_id):
    return fetch_one("SELECT id, name, email FROM users WHERE id = %s", (user_id,))


def get_all_users():
    return fetch_all("SELECT id, name, email FROM users ORDER BY name")


# ==================================================================
# GROUPS
# ==================================================================
def create_group(group_name, created_by):
    """Create the group and automatically add the creator as a member."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO `groups` (group_name, created_by) VALUES (%s, %s)",
            (group_name, created_by),
        )
        group_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
            (group_id, created_by),
        )
        conn.commit()
        return group_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_group(group_id):
    return fetch_one(
        """SELECT g.id, g.group_name, g.created_by, u.name AS created_by_name
           FROM `groups` g JOIN users u ON u.id = g.created_by
           WHERE g.id = %s""",
        (group_id,),
    )


def get_groups_for_user(user_id):
    return fetch_all(
        """SELECT g.id, g.group_name, g.created_by
           FROM `groups` g JOIN group_members gm ON gm.group_id = g.id
           WHERE gm.user_id = %s ORDER BY g.id DESC""",
        (user_id,),
    )


def get_members(group_id):
    return fetch_all(
        """SELECT u.id, u.name, u.email
           FROM group_members gm JOIN users u ON u.id = gm.user_id
           WHERE gm.group_id = %s ORDER BY u.name""",
        (group_id,),
    )


def is_member(group_id, user_id):
    row = fetch_one(
        "SELECT id FROM group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id),
    )
    return row is not None


def add_member(group_id, user_id):
    return execute_query(
        "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
        (group_id, user_id),
    )


# ==================================================================
# EXPENSES
# ==================================================================
def create_expense(group_id, description, amount, paid_by, expense_date, shares):
    """
    Save the expense and every person's share in ONE transaction:
    either everything is saved or nothing is.
    shares = {user_id: Decimal amount}
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO expenses (group_id, description, amount, paid_by, date)
               VALUES (%s, %s, %s, %s, %s)""",
            (group_id, description, amount, paid_by, expense_date),
        )
        expense_id = cursor.lastrowid
        for user_id, share in shares.items():
            cursor.execute(
                """INSERT INTO expense_splits (expense_id, user_id, share_amount)
                   VALUES (%s, %s, %s)""",
                (expense_id, user_id, share),
            )
        conn.commit()
        return expense_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_expense(expense_id):
    return fetch_one(
        """SELECT e.id, e.group_id, e.description, e.amount, e.paid_by,
                  u.name AS paid_by_name, e.date
           FROM expenses e JOIN users u ON u.id = e.paid_by
           WHERE e.id = %s""",
        (expense_id,),
    )


def get_expenses_by_group(group_id):
    return fetch_all(
        """SELECT e.id, e.group_id, e.description, e.amount, e.paid_by,
                  u.name AS paid_by_name, e.date
           FROM expenses e JOIN users u ON u.id = e.paid_by
           WHERE e.group_id = %s ORDER BY e.date DESC, e.id DESC""",
        (group_id,),
    )


def get_splits(expense_id):
    return fetch_all(
        """SELECT es.user_id, u.name, es.share_amount
           FROM expense_splits es JOIN users u ON u.id = es.user_id
           WHERE es.expense_id = %s""",
        (expense_id,),
    )


# ==================================================================
# BALANCE HELPERS (raw totals from the database)
# ==================================================================
def get_total_paid(group_id):
    rows = fetch_all(
        """SELECT paid_by AS user_id, SUM(amount) AS total
           FROM expenses WHERE group_id = %s GROUP BY paid_by""",
        (group_id,),
    )
    return {row["user_id"]: row["total"] for row in rows}


def get_total_owed(group_id):
    rows = fetch_all(
        """SELECT es.user_id, SUM(es.share_amount) AS total
           FROM expense_splits es JOIN expenses e ON e.id = es.expense_id
           WHERE e.group_id = %s GROUP BY es.user_id""",
        (group_id,),
    )
    return {row["user_id"]: row["total"] for row in rows}


def get_completed_settlement_totals(group_id):
    """Returns (sent, received) dictionaries for settlements already completed."""
    sent_rows = fetch_all(
        """SELECT from_user AS user_id, SUM(amount) AS total FROM settlements
           WHERE group_id = %s AND status = 'completed' GROUP BY from_user""",
        (group_id,),
    )
    received_rows = fetch_all(
        """SELECT to_user AS user_id, SUM(amount) AS total FROM settlements
           WHERE group_id = %s AND status = 'completed' GROUP BY to_user""",
        (group_id,),
    )
    sent = {row["user_id"]: row["total"] for row in sent_rows}
    received = {row["user_id"]: row["total"] for row in received_rows}
    return sent, received


# ==================================================================
# SETTLEMENTS
# ==================================================================
def replace_pending_settlements(group_id, payments):
    """Delete old pending settlements of the group and save the new ones."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM settlements WHERE group_id = %s AND status = 'pending'",
            (group_id,),
        )
        for payment in payments:
            cursor.execute(
                """INSERT INTO settlements (group_id, from_user, to_user, amount, status)
                   VALUES (%s, %s, %s, %s, 'pending')""",
                (group_id, payment["from_user"], payment["to_user"], payment["amount"]),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_settlements_by_group(group_id):
    return fetch_all(
        """SELECT s.id, s.group_id, s.from_user, fu.name AS from_name,
                  s.to_user, tu.name AS to_name, s.amount, s.status
           FROM settlements s
           JOIN users fu ON fu.id = s.from_user
           JOIN users tu ON tu.id = s.to_user
           WHERE s.group_id = %s ORDER BY s.id""",
        (group_id,),
    )


def get_settlement(settlement_id):
    return fetch_one("SELECT * FROM settlements WHERE id = %s", (settlement_id,))


def update_settlement_status(settlement_id, status):
    execute_query(
        "UPDATE settlements SET status = %s WHERE id = %s", (status, settlement_id)
    )
