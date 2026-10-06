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
