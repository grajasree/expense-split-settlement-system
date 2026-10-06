import { useSearchParams } from "react-router-dom";

/**
 * Keeps the selected group in the URL (?group=3) so links like
 * "/balances?group=3" open the right group directly.
 */
export default function useSelectedGroup(groups) {
  const [params, setParams] = useSearchParams();
  const fromUrl = Number(params.get("group")) || null;
  const selected = groups.some((g) => g.id === fromUrl) ? fromUrl : groups[0]?.id ?? null;

  const select = (id) => setParams(id ? { group: String(id) } : {}, { replace: true });
  return [selected, select];
}
