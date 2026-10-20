
/**
 * api.js - Centralised Axios service for the Flask backend.
 *
 * Backend URL is configured in frontend/.env using VITE_API_BASE_URL.
 * All functions return the response body from the Flask backend.
 */
import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:5000";

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Convert Axios errors into readable messages.
 */
export function getErrorMessage(error) {
  if (error?.response) {
    const { data, status } = error.response;

    if (data && typeof data.message === "string") {
      return data.message;
    }

    return `Server returned an error (status ${status}).`;
  }

  if (
    error?.code === "ECONNABORTED" ||
    error?.code === "ETIMEDOUT"
  ) {
    return "The request took too long. Please try again.";
  }

  if (error?.request) {
    return `Cannot reach the backend at ${API_BASE_URL}. Please check your connection and try again.`;
  }

  return error?.message || "Something went wrong.";
}

const send = (request) =>
  request.then((response) => response.data);

// ---------------- AUTH ----------------

export const registerUser = ({ name, email, password }) =>
  send(client.post("/api/auth/register", { name, email, password }));

export const loginUser = ({ email, password }) =>
  send(client.post("/api/auth/login", { email, password }));

export const getUsers = () =>
  send(client.get("/api/auth/users"));

export const getUser = (userId) =>
  send(client.get(`/api/auth/users/${userId}`));

// ---------------- GROUPS ----------------

export const createGroup = ({ group_name, created_by }) =>
  send(client.post("/api/groups", { group_name, created_by }));

export const getUserGroups = (userId) =>
  send(client.get(`/api/groups/user/${userId}`));

export const getGroup = (groupId) =>
  send(client.get(`/api/groups/${groupId}`));

export const addGroupMember = (groupId, payload) =>
  send(client.post(`/api/groups/${groupId}/members`, payload));

// ---------------- EXPENSES ----------------

export const addExpense = (payload) =>
  send(client.post("/api/expenses", payload));

export const getGroupExpenses = (groupId) =>
  send(client.get(`/api/expenses/group/${groupId}`));

export const getExpense = (expenseId) =>
  send(client.get(`/api/expenses/${expenseId}`));

// ---------------- BALANCES & SETTLEMENTS ----------------

export const getBalances = (groupId) =>
  send(client.get(`/api/settlements/balances/${groupId}`));

export const getSuggestedPayments = (groupId) =>
  send(client.get(`/api/settlements/suggest/${groupId}`));

export const generateSettlements = (groupId) =>
  send(client.post(`/api/settlements/generate/${groupId}`));

export const getGroupSettlements = (groupId) =>
  send(client.get(`/api/settlements/group/${groupId}`));

export const updateSettlementStatus = (settlementId, status) =>
  send(
    client.put(`/api/settlements/${settlementId}/status`, { status })
  );

export default client;
