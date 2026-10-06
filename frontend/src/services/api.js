/**
 * api.js - Centralised Axios service for the Flask backend.
 *
 * BACKEND URL: change it in ".env" (VITE_API_BASE_URL) - nowhere else.
 *
 * Every backend response has this shape:
 *   success: { success: true,  message: "...", data: ... }
 *   error:   { success: false, message: "..." }
 * Each function below returns that body, so callers use `res.data` and `res.message`.
 *
 * The backend has NO token / JWT / session. Login simply returns the user object.
 */
import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

/** Turn any Axios error into a short, friendly sentence. */
export function getErrorMessage(error) {
  if (error?.response) {
    const { data, status } = error.response;
    if (data && typeof data.message === "string") return data.message; // message written by the Flask backend
    return `Server returned an error (status ${status}).`;
  }
  if (error?.code === "ECONNABORTED") return "The server took too long to respond. Please try again.";
  if (error?.request) {
    return `Cannot reach the backend at ${API_BASE_URL}. Please make sure the Flask server is running.`;
  }
  return error?.message || "Something went wrong.";
}

const send = (request) => request.then((response) => response.data);

// ---------------- AUTH  (routes/auth_routes.py) ----------------
export const registerUser = ({ name, email, password }) =>
  send(client.post("/api/auth/register", { name, email, password }));

export const loginUser = ({ email, password }) =>
  send(client.post("/api/auth/login", { email, password }));

export const getUsers = () => send(client.get("/api/auth/users"));
export const getUser = (userId) => send(client.get(`/api/auth/users/${userId}`));

// ---------------- GROUPS  (routes/group_routes.py) ----------------
export const createGroup = ({ group_name, created_by }) =>
  send(client.post("/api/groups", { group_name, created_by }));

export const getUserGroups = (userId) => send(client.get(`/api/groups/user/${userId}`));
export const getGroup = (groupId) => send(client.get(`/api/groups/${groupId}`));

/** payload is { user_id } OR { email } */
export const addGroupMember = (groupId, payload) =>
  send(client.post(`/api/groups/${groupId}/members`, payload));

// ---------------- EXPENSES  (routes/expense_routes.py) ----------------
/**
 * payload: {
 *   group_id, description, amount, paid_by, date?, split_type: "equal"|"percentage"|"custom",
 *   participants?: [ids]                         (equal)
 *   splits?: [{user_id, percentage}|{user_id, amount}]   (percentage / custom)
 * }
 */
export const addExpense = (payload) => send(client.post("/api/expenses", payload));
export const getGroupExpenses = (groupId) => send(client.get(`/api/expenses/group/${groupId}`));
export const getExpense = (expenseId) => send(client.get(`/api/expenses/${expenseId}`));

// ---------------- BALANCES & SETTLEMENTS  (routes/settlement_routes.py) ----------------
export const getBalances = (groupId) => send(client.get(`/api/settlements/balances/${groupId}`));
export const getSuggestedPayments = (groupId) => send(client.get(`/api/settlements/suggest/${groupId}`));
export const generateSettlements = (groupId) => send(client.post(`/api/settlements/generate/${groupId}`));
export const getGroupSettlements = (groupId) => send(client.get(`/api/settlements/group/${groupId}`));
export const updateSettlementStatus = (settlementId, status) =>
  send(client.put(`/api/settlements/${settlementId}/status`, { status }));

export default client;
