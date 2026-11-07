import DependencyGraph from "./components/DependencyGraph";
import sampleGraph from "./sample_graph.json";

function App() {
  const s = sampleGraph.stats;
  return (
    <div style={{ padding: 16, fontFamily: "sans-serif" }}>
      <h1>Codebase X-Ray</h1>
      <p>
        {s.files} files · {s.functions} functions · {s.calls} calls · {s.unused} unused
      </p>
      <DependencyGraph graphData={sampleGraph} />
    </div>
  );
}

export default App;