import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import useUserGroups from "../hooks/useUserGroups";
import useSelectedGroup from "../hooks/useSelectedGroup";
import {
  generateSettlements, getGroupSettlements, getSuggestedPayments,
  updateSettlementStatus, getErrorMessage,
} from "../services/api";
import { formatCurrency } from "../utils/format";
import PageHeader from "../components/PageHeader";
import GroupSelect from "../components/GroupSelect";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";
import NoGroups from "../components/NoGroups";
import StatusBadge from "../components/StatusBadge";
import StatCard from "../components/StatCard";
import ConfirmDialog from "../components/ConfirmDialog";

export default function Settlements() {
  const { user } = useAuth();
  const toast = useToast();
  const { groups, loading: groupsLoading, error: groupsError } = useUserGroups(user.id);
  const [groupId, selectGroup] = useSelectedGroup(groups);

  const [payments, setPayments] = useState([]);   // who owes whom (calculated by backend)
  const [saved, setSaved] = useState([]);         // settlements stored in the database
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const [confirmGenerate, setConfirmGenerate] = useState(false);
  const [statusChange, setStatusChange] = useState(null); // { settlement, status }
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!groupId) return;
    setLoading(true);
    setError("");
    try {
      const [suggest, list] = await Promise.all([getSuggestedPayments(groupId), getGroupSettlements(groupId)]);
      setPayments(suggest.data.payments);
      setSaved(list.data.settlements);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [groupId]);

  useEffect(() => {
    load();
  }, [load]);

  const handleGenerate = async () => {
    setBusy(true);
    try {
      const response = await generateSettlements(groupId);
      toast(response.message);
      setConfirmGenerate(false);
      await load();
    } catch (err) {
      setConfirmGenerate(false);
      toast(getErrorMessage(err), "error");
    } finally {
      setBusy(false);
    }
  };

  const handleStatus = async () => {
    setBusy(true);
    try {
      const response = await updateSettlementStatus(statusChange.settlement.id, statusChange.status);
      toast(response.message);
      setStatusChange(null);
      await load();
    } catch (err) {
      setStatusChange(null);
      toast(getErrorMessage(err), "error");
    } finally {
      setBusy(false);
    }
  };

  if (groupsLoading) return <Loader text="Loading groups..." />;
  if (groupsError) return <ErrorBanner message={groupsError} />;
  if (groups.length === 0) return <NoGroups />;

  const pending = saved.filter((s) => s.status === "pending");
  const completed = saved.filter((s) => s.status === "completed");
  const sumOf = (list) => list.reduce((t, s) => t + s.amount, 0);
  const visible = filter === "all" ? saved : saved.filter((s) => s.status === filter);

  return (
    <>
      <PageHeader title="Settlements" subtitle="See who owes whom and track the payments">
        <GroupSelect groups={groups} value={groupId} onChange={selectGroup} />
      </PageHeader>

      <ErrorBanner message={error} onRetry={load} />
      {loading ? (
        <Loader text="Calculating settlements..." />
      ) : (
        !error && (
          <>
            <div className="grid-cards">
              <StatCard icon="⏳" label="Pending" value={`${pending.length} · ${formatCurrency(sumOf(pending))}`} tone="amber" />
              <StatCard icon="✅" label="Completed" value={`${completed.length} · ${formatCurrency(sumOf(completed))}`} tone="green" />
            </div>

            <section className="card">
              <div className="card-head">
                <h2 className="card-title">Who owes whom</h2>
                <button className="btn btn-primary" disabled={payments.length === 0} onClick={() => setConfirmGenerate(true)}>
                  Save as pending settlements
                </button>
              </div>
              {payments.length === 0 ? (
                <EmptyState icon="🎉" title="All settled!" text="Nobody owes anything in this group right now." />
              ) : (
                <ul className="owe-list">
                  {payments.map((p, index) => (
                    <li key={index}>
                      <span className="owe-from">{p.from_name}</span>
                      <span className="owe-arrow">owes →</span>
                      <span className="owe-to">{p.to_name}</span>
                      <strong className="owe-amount">{formatCurrency(p.amount)}</strong>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="card">
              <div className="card-head">
                <h2 className="card-title">Settlement status</h2>
                <div className="tabs compact">
                  {["all", "pending", "completed"].map((f) => (
                    <button key={f} className={`tab ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                      {f.charAt(0).toUpperCase() + f.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              {visible.length === 0 ? (
                <EmptyState icon="🤝" title="No settlements to show"
                  text={saved.length === 0 ? "Click “Save as pending settlements” above to create them." : "Nothing in this filter."} />
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>#</th><th>From</th><th>To</th><th className="num">Amount</th><th>Status</th><th></th></tr></thead>
                    <tbody>
                      {visible.map((s) => (
                        <tr key={s.id}>
                          <td>{s.id}</td><td>{s.from_name}</td><td>{s.to_name}</td>
                          <td className="num">{formatCurrency(s.amount)}</td>
                          <td><StatusBadge status={s.status} /></td>
                          <td className="num">
                            {s.status === "pending" ? (
                              <button className="btn btn-sm btn-success" onClick={() => setStatusChange({ settlement: s, status: "completed" })}>Mark completed</button>
                            ) : (
                              <button className="btn btn-sm btn-outline" onClick={() => setStatusChange({ settlement: s, status: "pending" })}>Mark pending</button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )
      )}

      <ConfirmDialog
        open={confirmGenerate}
        title="Save settlements"
        message="This saves the “who owes whom” list as pending settlements. Any existing pending settlements of this group will be replaced (completed ones are kept)."
        confirmText="Save settlements"
        loading={busy}
        onConfirm={handleGenerate}
        onCancel={() => setConfirmGenerate(false)}
      />
      <ConfirmDialog
        open={Boolean(statusChange)}
        title={`Mark as ${statusChange?.status}`}
        message={statusChange ? `${statusChange.settlement.from_name} → ${statusChange.settlement.to_name}, ${formatCurrency(statusChange.settlement.amount)}: mark this settlement as ${statusChange.status}?` : ""}
        confirmText="Yes, update"
        loading={busy}
        onConfirm={handleStatus}
        onCancel={() => setStatusChange(null)}
      />
    </>
  );
}
