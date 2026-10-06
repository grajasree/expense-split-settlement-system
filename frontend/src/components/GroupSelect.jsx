export default function GroupSelect({ groups, value, onChange, label = "Group" }) {
  return (
    <label className="group-select">
      <span>{label}</span>
      <select value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
        {groups.map((group) => (
          <option key={group.id} value={group.id}>
            {group.group_name}
          </option>
        ))}
      </select>
    </label>
  );
}
