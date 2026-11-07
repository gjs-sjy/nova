// Side panel showing the clicked function: its code, who calls it, and what it calls.
// (The two AI buttons get added in Milestone 6.)

function shortName(nodeId) {
  return nodeId.split("::")[1] + "()"; // "utils.py::calculate_total" -> "calculate_total()"
}

function IdList({ title, ids, color }) {
  return (
    <div style={{ marginTop: 12 }}>
      <strong style={{ color }}>{title}</strong>
      {ids.length === 0 ? (
        <div style={{ color: "#94a3b8" }}>nothing</div>
      ) : (
        <ul style={{ margin: "4px 0", paddingLeft: 20 }}>
          {ids.map((id) => (
            <li key={id} title={id}>
              {shortName(id)} <span style={{ color: "#94a3b8" }}>{id.split("::")[0]}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CodePanel({ node, impact, loading, error }) {
  if (!node) {
    return <div style={panelStyle}>Click a function in the graph to see its code.</div>;
  }

  return (
    <div style={panelStyle}>
      <h2 style={{ margin: "0 0 4px" }}>
        {node.class_name ? `${node.class_name}.` : ""}
        {node.name}()
      </h2>
      <div style={{ color: "#94a3b8" }}>
        {node.file} · lines {node.start_line}–{node.end_line}
        {node.is_entry_point && <span style={{ color: "#22c55e" }}> · entry point</span>}
        {node.is_unused && <span style={{ color: "#ef4444" }}> · unused</span>}
      </div>

      <pre
        style={{
          background: "#0f172a",
          color: "#e2e8f0",
          padding: 12,
          borderRadius: 6,
          overflowX: "auto",
          fontSize: 12,
          fontFamily: "monospace",
        }}
      >
        {node.code}
      </pre>

      {loading && <div>Loading dependencies…</div>}
      {error && <div style={{ color: "#ef4444" }}>{error}</div>}
      {impact && (
        <>
          <IdList title="Called by" ids={impact.direct_callers} color="#ef4444" />
          <IdList title="Calls" ids={impact.calls} color="#3b82f6" />
          <IdList
            title={`Could break if deleted (${impact.all_affected.length})`}
            ids={impact.all_affected}
            color="#ef4444"
          />
        </>
      )}
    </div>
  );
}

const panelStyle = {
  width: 380,
  flexShrink: 0,
  height: "80vh",
  overflowY: "auto",
  padding: 16,
  boxSizing: "border-box",
  background: "#1e293b",
  color: "white",
  borderRadius: 8,
  fontSize: 14,
};

export default CodePanel;
