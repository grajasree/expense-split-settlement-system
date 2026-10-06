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
