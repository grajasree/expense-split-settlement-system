import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import useUserGroups from "../hooks/useUserGroups";
import { createGroup, getErrorMessage } from "../services/api";
import PageHeader from "../components/PageHeader";
import Modal from "../components/Modal";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";
import EmptyState from "../components/EmptyState";

export default function Groups() {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const { groups, loading, error, reload } = useUserGroups(user.id);

  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [apiError, setApiError] = useState("");
  const [saving, setSaving] = useState(false);

  const closeModal = () => {
    setModalOpen(false);
    setName("");
    setFieldError("");
    setApiError("");
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    setApiError("");
    if (!name.trim()) {
      setFieldError("Group name is required");
      return;
    }
    setFieldError("");
    setSaving(true);
    try {
      const response = await createGroup({ group_name: name.trim(), created_by: user.id });
      toast(response.message);
      closeModal();
      navigate(`/groups/${response.data.id}`);
    } catch (err) {
      setApiError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader title="Groups" subtitle="Groups you created or were added to">
        <button className="btn btn-primary" onClick={() => setModalOpen(true)}>+ Create Group</button>
      </PageHeader>

      <ErrorBanner message={error} onRetry={reload} />
      {loading ? (
        <Loader text="Loading groups..." />
      ) : groups.length === 0 && !error ? (
        <EmptyState icon="👥" title="No groups yet" text="Create a group like “Goa Trip” or “Flat Expenses”.">
          <button className="btn btn-primary" onClick={() => setModalOpen(true)}>Create your first group</button>
        </EmptyState>
      ) : (
        <div className="grid-groups">
          {groups.map((group) => (
            <div className="card group-card" key={group.id}>
              <div className="group-avatar">{group.group_name.charAt(0).toUpperCase()}</div>
              <h3>{group.group_name}</h3>
              <p className="muted">{group.created_by === user.id ? "Created by you" : "You are a member"}</p>
              <div className="group-card-actions">
                <Link to={`/groups/${group.id}`} className="btn btn-sm btn-primary">View Details</Link>
                <Link to={`/expenses/new?group=${group.id}`} className="btn btn-sm btn-outline">Add Expense</Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} title="Create a new group" onClose={closeModal}>
        <form onSubmit={handleCreate} noValidate>
          <ErrorBanner message={apiError} />
          <div className="field">
            <label htmlFor="group_name">Group name</label>
            <input id="group_name" autoFocus placeholder="e.g. Goa Trip" value={name} onChange={(e) => setName(e.target.value)} />
            {fieldError && <span className="field-error">{fieldError}</span>}
          </div>
          <p className="muted small">You will be added to the group automatically.</p>
          <div className="modal-actions">
            <button type="button" className="btn btn-outline" onClick={closeModal} disabled={saving}>Cancel</button>
            <button className="btn btn-primary" disabled={saving}>
              {saving && <span className="spinner sm" />} Create Group
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
