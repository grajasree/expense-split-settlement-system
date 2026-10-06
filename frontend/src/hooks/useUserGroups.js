import { useCallback, useEffect, useState } from "react";
import { getUserGroups, getErrorMessage } from "../services/api";

/** Loads the groups the logged-in user belongs to. */
export default function useUserGroups(userId) {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await getUserGroups(userId);
      setGroups(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { groups, loading, error, reload };
}
