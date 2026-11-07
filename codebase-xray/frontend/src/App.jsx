import { useState } from "react";
import DependencyGraph from "./components/DependencyGraph";
import Upload from "./components/Upload";
import sampleGraph from "./sample_graph.json";

function App() {
  // Starts with the fake sample data; replaced by the real /upload response.
  const [graphData, setGraphData] = useState(sampleGraph);
  const s = graphData.stats;

  return (
    <div style={{ padding: 16, fontFamily: "sans-serif" }}>
      <h1>Codebase X-Ray</h1>
      <Upload onUploaded={setGraphData} />
      <p>
        {s.files} files · {s.functions} functions · {s.calls} calls · {s.unused} unused
        {s.skipped_files.length > 0 && ` · skipped: ${s.skipped_files.join(", ")}`}
      </p>
      {/* key = project_id so the graph re-fits the view for each new upload */}
      <DependencyGraph key={graphData.project_id} graphData={graphData} />
    </div>
  );
}

export default App;
