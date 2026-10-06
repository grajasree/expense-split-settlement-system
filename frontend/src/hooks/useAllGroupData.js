import { useCallback, useEffect, useState } from "react";
import {
  getUserGroups,
  getGroupExpenses,
  getBalances,
  getGroupSettlements,
  getErrorMessage,
} from "../services/api";

/**
 * Loads, for every group of the user, the real data from the backend:
 * expenses, balances and settlements. Used by Dashboard and History pages.
 */
export default function useAllGroupData(userId) {
  const [state, setState] = useState({ loading: true, error: "", items: [] });

  const reload = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const groups = (await getUserGroups(userId)).data;
      const items = await Promise.all(
        groups.map(async (group) => {
          const [exp, bal, set] = await Promise.all([
            getGroupExpenses(group.id),
            getBalances(group.id),
            getGroupSettlements(group.id),
          ]);
          return {
            group,
            expenses: exp.data.expenses,
            totalSpent: exp.data.total_spent,
            balances: bal.data.balances,
            settlements: set.data.settlements,
          };
        })
      );
      setState({ loading: false, error: "", items });
    } catch (err) {
      setState({ loading: false, error: getErrorMessage(err), items: [] });
    }
  }, [userId]);

  useEffect(() => {
    reload();
  }, [reload]);

  return { ...state, reload };
}
