<template>
  <div class="logs-panel">
    <h3>Jurnal comenzi trimise</h3>

    <div class="filter-section">
      <input
        v-model="filterIp"
        placeholder="Filtrează după IP (ex: 192.168.100.2)"
      />
      <button @click="loadLogs">Filtrează</button>
      <button @click="resetFilter" v-if="filterIp">Resetează</button>
      <button @click="clearLogs" class="danger">Șterge toate logurile</button>
    </div>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="logs.length === 0 && !error">
      <p>Nu există comenzi înregistrate.</p>
    </div>

    <div class="logs-table-scroll">
      <table v-if="logs.length > 0">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>IP</th>
            <th>User</th>
            <th>Comandă</th>
            <th>Output</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ log.timestamp }}</td>
            <td>{{ log.ip }}</td>
            <td>{{ log.username }}</td>
            <td><pre>{{ log.command }}</pre></td>
            <td class="output-cell"><pre>{{ log.output }}</pre></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LogsPanel',
  data() {
    return {
      logs: [],
      filterIp: '',
      error: ''
    }
  },
  methods: {
    async loadLogs() {
      try {
        this.error = ''
        let url = 'http://localhost:8000/logs'
        if (this.filterIp.trim()) {
          url += `?ip=${encodeURIComponent(this.filterIp.trim())}`
        }
        const response = await axios.get(url)
        this.logs = response.data
      } catch (err) {
        this.error = 'Eroare la încărcarea logurilor: ' + err.message
        this.logs = []
      }
    },
    resetFilter() {
      this.filterIp = ''
      this.loadLogs()
    },
    async clearLogs() {
      if (!confirm("Ești sigur că vrei să ștergi toate logurile?")) return
      try {
        await axios.delete('http://localhost:8000/logs')
        this.logs = []
      } catch (err) {
        this.error = 'Eroare la ștergerea logurilor: ' + err.message
      }
    }
  },
  created() {
    this.loadLogs()
  }
}
</script>

<style scoped>
.logs-panel {
  display: flex;
  flex-direction: column;
}

.filter-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  flex: 1;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #1e3a8a;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #1c3574;
}

button.danger {
  background-color: #c0392b;
}

.error {
  color: red;
  font-weight: bold;
  margin-bottom: 1rem;
}

.logs-table-scroll {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 0.9rem;
}

th, td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  vertical-align: top;
  text-align: left;
  word-wrap: break-word;
}

th:nth-child(1), td:nth-child(1) { width: 140px; } /* Timestamp */
th:nth-child(2), td:nth-child(2) { width: 120px; } /* IP */
th:nth-child(3), td:nth-child(3) { width: 100px; } /* User */
th:nth-child(4), td:nth-child(4) { width: 120px; } /* Command */
th:nth-child(5), td:nth-child(5) { width: auto; }   /* Output */

.output-cell {
  white-space: pre-wrap;
}
</style>

