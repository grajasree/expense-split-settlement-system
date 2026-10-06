import { Link } from "react-router-dom";
import EmptyState from "./EmptyState";

export default function NoGroups() {
  return (
    <EmptyState icon="👥" title="No groups yet" text="Create a group (or ask a friend to add you) to get started.">
      <Link to="/groups" className="btn btn-primary">
        Go to Groups
      </Link>
    </EmptyState>
  );
}
