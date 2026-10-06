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
