<template>
  <div class="network-map">
    <h3>Hartă topologie rețea</h3>
    <button @click="drawNetwork" class="refresh-btn">Regenerare topologie</button>
    <div ref="networkContainer" class="vis-container"></div>

    <div v-if="selectedNode" class="node-details">
      <h4>Detalii Nod</h4>
      <p><strong>ID:</strong> {{ selectedNode.id }}</p>
      <p><strong>Tip:</strong> {{ selectedNode.type }}</p>
      <p v-if="selectedNode.ip"><strong>IP:</strong> {{ selectedNode.ip }}</p>
      <p v-if="selectedNode.note"><strong>Notă:</strong> {{ selectedNode.note }}</p>

      <div v-if="selectedNode.interfaces">
        <p><strong>Interfețe:</strong></p>
        
          <p v-for="(ip, iface) in selectedNode.interfaces" :key="iface">
            {{ iface }}: {{ ip }}
          </p>
        
      </div>

      <div v-if="selectedNode.areas && selectedNode.areas.length">
        <p><strong>Arii OSPF:</strong> {{ selectedNode.areas.join(', ') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Network } from 'vis-network/peer'

export default {
  name: 'NetworkMap',
  setup() {
    const networkContainer = ref(null)
    const selectedNode = ref(null)
    let network = null

    const getNodeStyle = (type) => {
      switch (type) {
        case 'Router':
          return { shape: 'box', color: '#6baed6' }
        case 'VPCS':
          return { shape: 'ellipse', color: '#f4a261' }
        case 'Switch':
          return { shape: 'ellipse', color: '#a1d99b' }
        default:
          return { shape: 'ellipse', color: '#cccccc' }
      }
    }

    const drawNetwork = async () => {
      try {
        const response = await axios.get('http://localhost:8000/topology_map')
        const { nodes, edges } = response.data

        const positionMap = {
          "R2": { x: 0, y: 0 },
          "R1": { x: -200, y: 200 },
          "R3": { x: 200, y: 200 },
          "VPCS-10.0.1.0/24": { x: -200, y: 400 },
          "VPCS-10.0.2.0/24": { x: 200, y: 400 }
        }

        const visNodes = nodes.map(n => {
          const style = getNodeStyle(n.type)
          const fixedPosition = positionMap[n.id] || {}
          return {
            id: n.id,
            label: n.id,
            title: n.ip || '',
            shape: style.shape,
            color: style.color,
            x: fixedPosition.x,
            y: fixedPosition.y,
            fixed: fixedPosition.x !== undefined && fixedPosition.y !== undefined
          }
        })

        const visEdges = edges.map(e => ({
          from: e.from,
          to: e.to,
          label: e.label,
          arrows: 'to',
          smooth: false,
          font: { align: 'middle', size: 10 }
        }))

        const data = {
          nodes: visNodes,
          edges: visEdges
        }

        const options = {
          layout: {
            hierarchical: false
          },
          interaction: {
            hover: true,
            dragNodes: true,
            zoomView: true,
            selectable: true
          },
          physics: {
            enabled: false
          }
        }

        network = new Network(networkContainer.value, data, options)

        network.on('click', params => {
          const nodeId = params.nodes[0]
          if (nodeId) {
            const found = nodes.find(n => n.id === nodeId)
            selectedNode.value = found
          } else {
            selectedNode.value = null
          }
        })

      } catch (error) {
        console.error('Eroare la încărcarea topologiei:', error)
      }
    }

    onMounted(drawNetwork)

    return {
      networkContainer,
      selectedNode,
      drawNetwork
    }
  }
}
</script>

<style scoped>
.network-map {
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 8px;
}
.vis-container {
  height: 500px;
  border: 1px solid #ccc;
  margin-bottom: 1rem;
}
.node-details {
  background-color: #eef;
  padding: 1rem;
  border-radius: 5px;
}
.refresh-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  background-color: #1e3a8a;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.refresh-btn:hover {
  background-color: #1c3574;
}
</style>

