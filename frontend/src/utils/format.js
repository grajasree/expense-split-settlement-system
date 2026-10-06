const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
});

export const formatCurrency = (value) => currencyFormatter.format(Number(value) || 0);

/** "2025-01-20" -> "20 Jan 2025" */
export function formatDate(value) {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  if (isNaN(date)) return value;
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

/** Today's date as YYYY-MM-DD in the user's local time (format the backend expects). */
export function todayISO() {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

export const isValidEmail = (email) => /^[\w.\-+]+@[\w-]+\.[\w.-]+$/.test(email);

/** Build and download a CSV file in the browser. rows = array of arrays. */
export function downloadCsv(filename, headers, rows) {
  const escape = (cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`;
  const csv = [headers, ...rows].map((row) => row.map(escape).join(",")).join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
