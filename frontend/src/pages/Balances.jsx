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
