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
