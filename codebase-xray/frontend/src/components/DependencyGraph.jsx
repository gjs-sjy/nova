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

function DependencyGraph({ graphData }) {
  const { nodes: layoutNodes, edges: layoutEdges } = useMemo(() => {
    const rfNodes = graphData.nodes.map((n) => ({
      id: n.id,
      data: { label: `${n.name}()\n${n.file}` },
      style: {
        width: NODE_WIDTH,
        whiteSpace: "pre-line",
        fontSize: 12,
        background: "#1e293b",
        color: "white",
        borderRadius: 8,
        border: n.is_unused
          ? "2px solid #ef4444"
          : n.is_entry_point
          ? "2px solid #22c55e"
          : "1px solid #475569",
      },
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

  return (
    <div style={{ width: "100%", height: "80vh", border: "1px solid #ddd" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default DependencyGraph;