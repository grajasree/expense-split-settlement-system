export default function Loader({ text = "Loading..." }) {
  return (
    <div className="loader-box">
      <span className="spinner" />
      <p>{text}</p>
    </div>
  );
}
