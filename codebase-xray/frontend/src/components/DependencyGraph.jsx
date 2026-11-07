import { ReactFlow, Background, Controls, MarkerType } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import dagre from 'dagre'

const NODE_WIDTH = 180
const NODE_HEIGHT = 50

// One background color per file. If there are more files than colors, we loop around.
const FILE_COLORS = ['#3b5bdb', '#2b8a3e', '#9c36b5', '#e8590c', '#0c8599', '#c2255c', '#5f3dc4', '#66a80f']

// Use dagre to work out an x/y position for every node (top-to-bottom layout).
function layout(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setGraph({ rankdir: 'TB', nodesep: 40, ranksep: 70 })
  g.setDefaultEdgeLabel(() => ({}))

  nodes.forEach((n) => g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT }))
  edges.forEach((e) => g.setEdge(e.source, e.target))
  dagre.layout(g)

  // dagre gives the CENTER of each node; React Flow wants the TOP-LEFT corner.
  return nodes.map((n) => {
    const pos = g.node(n.id)
    return { ...n, position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 } }
  })
}

// Turn the backend's contract format into the format React Flow expects.
function toReactFlow(graphData) {
  const files = [...new Set(graphData.nodes.map((n) => n.file))]

  const nodes = graphData.nodes.map((n) => {
    let border = '1px solid #222'
    if (n.is_unused) border = '3px solid #ff4d4f'
    if (n.is_entry_point) border = '3px solid #52c41a'

    return {
      id: n.id,
      data: { label: `${n.name}\n${n.file}` },
      style: {
        width: NODE_WIDTH,
        background: FILE_COLORS[files.indexOf(n.file) % FILE_COLORS.length],
        color: 'white',
        border,
        borderRadius: 8,
        fontSize: 12,
        whiteSpace: 'pre-line', // lets the "\n" in the label become a line break
      },
    }
  })

  const edges = graphData.edges.map((e) => ({
    id: `${e.source}->${e.target}`,
    source: e.source,
    target: e.target,
    markerEnd: { type: MarkerType.ArrowClosed },
  }))

  return { nodes: layout(nodes, edges), edges }
}

export default function DependencyGraph({ graphData }) {
  const { nodes, edges } = toReactFlow(graphData)

  return (
    <ReactFlow nodes={nodes} edges={edges} fitView colorMode="dark">
      <Background />
      <Controls />
    </ReactFlow>
  )
}
