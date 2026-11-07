import { useRef, useState } from "react";
import axios from "axios";
import DependencyGraph from "./components/DependencyGraph";
import Upload from "./components/Upload";
import CodePanel from "./components/CodePanel";
import sampleGraph from "./sample_graph.json";

const API_URL = "http://localhost:8000";

function App() {
  // Starts with the fake sample data; replaced by the real /upload response.
  const [graphData, setGraphData] = useState(sampleGraph);
  const [selectedNode, setSelectedNode] = useState(null); // the clicked function (contract node)
  const [impact, setImpact] = useState(null); // the /impact response for it
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [aiAnswer, setAiAnswer] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const latestClick = useRef(null); // ignore old answers if you click quickly

  function clearSelection() {
    latestClick.current = null;
    setSelectedNode(null);
    setImpact(null);
    setError(null);
    setAiAnswer(null);
    setAiLoading(false);
  }

  // mode is "explain" or "impact". The backend builds the AI context itself.
  async function handleAsk(mode) {
    const nodeId = selectedNode.id;
    setAiAnswer(null);
    setAiLoading(true);
    try {
      const response = await axios.post(`${API_URL}/explain`, {
        project_id: graphData.project_id,
        node_id: nodeId,
        mode,
      });
      if (latestClick.current === nodeId) setAiAnswer(response.data.answer);
    } catch (err) {
      if (latestClick.current !== nodeId) return;
      if (err.response) {
        setAiAnswer(err.response.data.detail || "The AI request failed.");
      } else {
        setAiAnswer("Can't reach the backend. Is it running on port 8000?");
      }
    } finally {
      if (latestClick.current === nodeId) setAiLoading(false);
    }
  }

  function handleUploaded(data) {
    clearSelection();
    setGraphData(data);
  }

  async function handleNodeClick(nodeId) {
    latestClick.current = nodeId;
    setSelectedNode(graphData.nodes.find((n) => n.id === nodeId));
    setImpact(null);
    setError(null);
    setAiAnswer(null);
    setAiLoading(false);
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/impact`, {
        project_id: graphData.project_id,
        node_id: nodeId,
      });
      if (latestClick.current === nodeId) setImpact(response.data);
    } catch (err) {
      if (latestClick.current !== nodeId) return;
      if (err.response) {
        setError(err.response.data.detail || "Could not load dependencies.");
      } else {
        setError("Can't reach the backend. Is it running on port 8000?");
      }
    } finally {
      if (latestClick.current === nodeId) setLoading(false);
    }
  }

  const s = graphData.stats;

  return (
    <div style={{ padding: 16, fontFamily: "sans-serif" }}>
      <h1>Codebase X-Ray</h1>
      <Upload onUploaded={handleUploaded} />
      <p>
        {s.files} files · {s.functions} functions · {s.calls} calls · {s.unused} unused
        {s.skipped_files.length > 0 && ` · skipped: ${s.skipped_files.join(", ")}`}
      </p>
      <div style={{ display: "flex", gap: 16 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* key = project_id so the graph re-fits the view for each new upload */}
          <DependencyGraph
            key={graphData.project_id}
            graphData={graphData}
            selectedId={selectedNode?.id}
            impact={impact}
            onNodeClick={handleNodeClick}
            onPaneClick={clearSelection}
          />
        </div>
        <CodePanel
          node={selectedNode}
          impact={impact}
          loading={loading}
          error={error}
          aiAnswer={aiAnswer}
          aiLoading={aiLoading}
          onAsk={handleAsk}
        />
      </div>
    </div>
  );
}

export default App;
