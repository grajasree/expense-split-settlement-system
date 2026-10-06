/**
 * AuthContext - keeps the logged-in user.
 * The backend does not issue tokens, so after a successful login we keep the
 * returned user ({id, name, email}) in localStorage and use it for all API calls.
 * On start-up we re-check the user with GET /api/auth/users/<id>.
 */
import { createContext, useContext, useEffect, useState } from "react";
import { getUser, loginUser, registerUser } from "../services/api";

const STORAGE_KEY = "expense_split_user";
const AuthContext = createContext(null);

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser);
  const [checking, setChecking] = useState(Boolean(readStoredUser()));

  // Make sure the saved user still exists in the database
  useEffect(() => {
    if (!user) {
      setChecking(false);
      return;
    }
    getUser(user.id)
      .catch((error) => {
        if (error?.response?.status === 404) logout(); // user no longer exists
      })
      .finally(() => setChecking(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email, password) => {
    const response = await loginUser({ email, password });
    localStorage.setItem(STORAGE_KEY, JSON.stringify(response.data));
    setUser(response.data);
    return response;
  };

  const register = (name, email, password) => registerUser({ name, email, password });

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, checking, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
