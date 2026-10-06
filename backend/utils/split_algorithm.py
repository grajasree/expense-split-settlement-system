"""
split_algorithm.py - Pure calculation logic (no database, no Flask).

Money is handled with Decimal (not float) so there are no rounding surprises
like 0.1 + 0.2 = 0.30000000000000004.

Contains:
  1. equal_split        - divide equally
  2. percentage_split   - divide by percentages
  3. custom_split       - divide by exact amounts
  4. calculate_balances - paid / owed / net balance for every user
  5. simplify_debts     - "who owes whom" using the fewest payments
"""
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, InvalidOperation

CENT = Decimal("0.01")


def to_money(value):
    """Convert any number/string to a Decimal with 2 decimal places."""
    try:
        return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid amount: {value}")


# ------------------------------------------------------------------
# 1. EQUAL SPLIT
# ------------------------------------------------------------------
def equal_split(total_amount, user_ids):
    """
    Split the total equally. If it doesn't divide exactly (e.g. 100 / 3),
    the extra paise are given one-by-one to the first users.
    100 among 3 -> 33.34, 33.33, 33.33
    """
    if not user_ids:
        raise ValueError("At least one participant is required for an equal split")

    total_cents = int(to_money(total_amount) * 100)
    base, remainder = divmod(total_cents, len(user_ids))

    shares = {}
    for index, user_id in enumerate(user_ids):
        cents = base + (1 if index < remainder else 0)
        shares[user_id] = (Decimal(cents) / 100).quantize(CENT)
    return shares


# ------------------------------------------------------------------
# 2. PERCENTAGE SPLIT
# ------------------------------------------------------------------
def percentage_split(total_amount, percentages):
    """
    percentages = {user_id: percent}, e.g. {1: 50, 2: 30, 3: 20}
    Percentages must add up to exactly 100.
    """
    if not percentages:
        raise ValueError("Percentages are required for a percentage split")

    total = to_money(total_amount)
    percent_values = {}
    for user_id, percent in percentages.items():
        try:
            value = Decimal(str(percent))
        except InvalidOperation:
            raise ValueError(f"Invalid percentage for user {user_id}")
        if value < 0:
            raise ValueError("Percentage cannot be negative")
        percent_values[user_id] = value

    if sum(percent_values.values()) != Decimal("100"):
        raise ValueError("Percentages must add up to 100")

    shares = {}
    for user_id, percent in percent_values.items():
        shares[user_id] = (total * percent / 100).quantize(CENT, rounding=ROUND_DOWN)

    # Give any leftover paise (from rounding down) to the first user
    leftover = total - sum(shares.values())
    first_user = next(iter(shares))
    shares[first_user] += leftover
    return shares


# ------------------------------------------------------------------
# 3. CUSTOM SPLIT
# ------------------------------------------------------------------
def custom_split(total_amount, amounts):
    """
    amounts = {user_id: amount}, e.g. {1: 500, 2: 300, 3: 200}
    The amounts must add up to the total.
    """
    if not amounts:
        raise ValueError("Amounts are required for a custom split")

    total = to_money(total_amount)
    shares = {}
    for user_id, amount in amounts.items():
        share = to_money(amount)
        if share < 0:
            raise ValueError("Split amount cannot be negative")
        shares[user_id] = share

    given_total = sum(shares.values())
    if given_total != total:
        raise ValueError(
            f"Custom amounts add up to {given_total}, but the expense total is {total}"
        )
    return shares


# ------------------------------------------------------------------
# 4. BALANCE CALCULATION
# ------------------------------------------------------------------
def calculate_balances(user_ids, paid, owed, settlements_sent, settlements_received):
    """
    For every user:
        net_balance = total_paid - total_owed - received + sent

    Positive net -> the group owes this user money.
    Negative net -> this user owes money to the group.

    'sent' / 'received' are settlements already marked completed. They reduce
    what is still pending.
    """
    result = {}
    for user_id in user_ids:
        total_paid = to_money(paid.get(user_id, 0))
        total_owed = to_money(owed.get(user_id, 0))
        sent = to_money(settlements_sent.get(user_id, 0))
        received = to_money(settlements_received.get(user_id, 0))

        result[user_id] = {
            "total_paid": total_paid,
            "total_owed": total_owed,
            "net_balance": total_paid - total_owed - received + sent,
        }
    return result


# ------------------------------------------------------------------
# 5. WHO OWES WHOM (debt simplification)
# ------------------------------------------------------------------
def simplify_debts(net_balances):
    """
    net_balances = {user_id: net_balance}
    Greedy method: the biggest debtor pays the biggest creditor, repeat.
    Returns a list like [{"from_user": 2, "to_user": 1, "amount": Decimal("100.00")}]
    """
    creditors = [[uid, bal] for uid, bal in net_balances.items() if bal > 0]
    debtors = [[uid, -bal] for uid, bal in net_balances.items() if bal < 0]
    creditors.sort(key=lambda item: item[1], reverse=True)
    debtors.sort(key=lambda item: item[1], reverse=True)

    payments = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        amount = min(debtors[i][1], creditors[j][1])
        if amount > 0:
            payments.append(
                {"from_user": debtors[i][0], "to_user": creditors[j][0], "amount": amount}
            )
        debtors[i][1] -= amount
        creditors[j][1] -= amount
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1
    return payments
