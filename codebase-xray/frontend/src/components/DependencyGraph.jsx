import { useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import dagre from "dagre";

const NODE_WIDTH = 180;
const NODE_HEIGHT = 50;

// Highlight colors when a function is clicked.
const SELECTED = "#facc15"; // yellow: the function you clicked
const AFFECTED = "#ef4444"; // red: callers / everything that could break
const CALLS = "#3b82f6"; // blue: what it calls

function layout(nodes, edges) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "TB", nodesep: 50, ranksep: 80 });
  g.setDefaultEdgeLabel(() => ({}));
  nodes.forEach((n) => g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT }));
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);
  return nodes.map((n) => {
    const pos = g.node(n.id);
    return { ...n, position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 } };
  });
}

// What color (if any) a node should be highlighted, given the current selection.
function highlightFor(nodeId, selectedId, impact) {
  if (!selectedId) return null; // nothing clicked: no highlighting
  if (nodeId === selectedId) return SELECTED;
  if (!impact) return null; // still waiting for /impact
  if (impact.all_affected.includes(nodeId)) return AFFECTED;
  if (impact.calls.includes(nodeId)) return CALLS;
  return "faded";
}

function nodeStyle(fn, highlight) {
  const style = {
    width: NODE_WIDTH,
    whiteSpace: "pre-line",
    fontSize: 12,
    background: "#1e293b",
    color: "white",
    borderRadius: 8,
    border: fn.is_unused
      ? "2px solid #ef4444"
      : fn.is_entry_point
      ? "2px solid #22c55e"
      : "1px solid #475569",
    transition: "opacity 0.2s, background 0.2s",
  };
  if (highlight === "faded") {
    style.opacity = 0.2;
  } else if (highlight) {
    style.background = highlight;
    style.color = highlight === SELECTED ? "#1e293b" : "white";
    style.fontWeight = "bold";
  }
  return style;
}

function DependencyGraph({ graphData, selectedId, impact, onNodeClick, onPaneClick }) {
  // Lay out the graph once per upload (dagre decides positions).
  const { nodes: layoutNodes, edges: layoutEdges } = useMemo(() => {
    const rfNodes = graphData.nodes.map((n) => ({
      id: n.id,
      data: { label: `${n.name}()\n${n.file}`, fn: n },
      style: nodeStyle(n, null),
    }));
    const rfEdges = graphData.edges.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
    }));
    return { nodes: layout(rfNodes, rfEdges), edges: rfEdges };
  }, [graphData]);

  // Keep nodes/edges in state so React Flow can apply drag (position) changes.
  const [nodes, setNodes, onNodesChange] = useNodesState(layoutNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutEdges);

  // Re-apply the dagre layout whenever new graph data arrives.
  useEffect(() => {
    setNodes(layoutNodes);
    setEdges(layoutEdges);
  }, [layoutNodes, layoutEdges, setNodes, setEdges]);

  // Re-color nodes and edges when the selection changes. Positions stay where you dragged them.
  useEffect(() => {
    setNodes((current) =>
      current.map((n) => ({
        ...n,
        style: nodeStyle(n.data.fn, highlightFor(n.id, selectedId, impact)),
      }))
    );
    setEdges((current) =>
      current.map((e) => {
        const from = highlightFor(e.source, selectedId, impact);
        const to = highlightFor(e.target, selectedId, impact);
        // An edge lights up when both ends are highlighted; it fades if either end is faded.
        const lit = selectedId && from && to && from !== "faded" && to !== "faded";
        const faded = from === "faded" || to === "faded";
        return {
          ...e,
          animated: Boolean(lit),
          style: lit
            ? { stroke: to === CALLS ? CALLS : AFFECTED, strokeWidth: 2 }
            : faded
            ? { opacity: 0.15 }
            : {},
        };
      })
    );
  }, [selectedId, impact, setNodes, setEdges]);

  return (
    <div style={{ width: "100%", height: "80vh", border: "1px solid #ddd" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => onNodeClick(node.id)}
        onPaneClick={onPaneClick}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default DependencyGraph;
