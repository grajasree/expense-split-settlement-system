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
