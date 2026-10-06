import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Groups from "./pages/Groups";
import GroupDetails from "./pages/GroupDetails";
import AddExpense from "./pages/AddExpense";
import Expenses from "./pages/Expenses";
import Balances from "./pages/Balances";
import Settlements from "./pages/Settlements";
import History from "./pages/History";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      {/* public pages */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* pages that need a logged-in user */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/groups" element={<Groups />} />
        <Route path="/groups/:groupId" element={<GroupDetails />} />
        <Route path="/expenses/new" element={<AddExpense />} />
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/balances" element={<Balances />} />
        <Route path="/settlements" element={<Settlements />} />
        <Route path="/history" element={<History />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
