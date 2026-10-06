/** Works for settlement status (pending/completed) and balance status (gets back/owes/settled). */
const TONES = {
  pending: "amber",
  completed: "green",
  "gets back": "green",
  owes: "red",
  settled: "gray",
};

export default function StatusBadge({ status }) {
  return <span className={`badge badge-${TONES[status] || "gray"}`}>{status}</span>;
}
