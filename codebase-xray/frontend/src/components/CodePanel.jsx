// Side panel showing the clicked function: its code, who calls it, what it calls,
// and two buttons that ask the AI to explain it.

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

function CodePanel({ node, impact, loading, error, aiAnswer, aiLoading, onAsk }) {
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

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button style={buttonStyle} disabled={aiLoading} onClick={() => onAsk("explain")}>
          Explain this
        </button>
        <button
          style={{ ...buttonStyle, background: "#b91c1c" }}
          disabled={aiLoading}
          onClick={() => onAsk("impact")}
        >
          What breaks if I delete this?
        </button>
      </div>
      {aiLoading && <div style={{ marginTop: 8 }}>Asking the AI…</div>}
      {aiAnswer && (
        <div
          style={{
            marginTop: 8,
            padding: 12,
            background: "#334155",
            borderRadius: 6,
            whiteSpace: "pre-wrap",
            lineHeight: 1.4,
          }}
        >
          {aiAnswer}
        </div>
      )}

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

const buttonStyle = {
  flex: 1,
  padding: "8px 10px",
  border: "none",
  borderRadius: 6,
  background: "#2563eb",
  color: "white",
  fontWeight: "bold",
  cursor: "pointer",
};

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
