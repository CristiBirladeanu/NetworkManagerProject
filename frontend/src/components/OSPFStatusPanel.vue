<template>
  <div class="ospf-status-panel">
    <h3>Status OSPF</h3>

    <form @submit.prevent="getOspfStatus">
      <select v-model="selectedDevice" @change="fillForm">
        <option disabled value="">Selectează un router</option>
        <option v-for="device in devices" :key="device.ip_address" :value="device.hostname">
          {{ device.hostname }}
        </option>
      </select>

      <input v-model="form.ip" placeholder="IP router" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />
      <button type="submit">Verifică OSPF</button>
    </form>

    <div v-if="status">
      <h4>Vecini OSPF:</h4>
      <pre>{{ status.neighbors }}</pre>
      <h4>Routing Table OSPF:</h4>
      <pre>{{ status.routes }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OSPFStatusPanel',
  props: ['devices'],
  data() {
    return {
      form: {
        ip: '',
        username: '',
        password: ''
      },
      selectedDevice: '',
      status: null
    }
  },
  methods: {
    async getOspfStatus() {
      try {
        const response = await axios.post('http://localhost:8000/ospf_status', this.form)
        this.status = response.data
      } catch (error) {
        this.status = { neighbors: '', routes: 'Eroare: ' + error.message }
      }
    },
    fillForm() {
      const selected = this.devices.find(d => d.hostname === this.selectedDevice)
      if (selected) {
        this.form.ip = selected.ip_address
        this.form.username = selected.username
        this.form.password = selected.password
      }
    }
  }
}
</script>

<style scoped>
.ospf-status-panel{
  background-color: #ffffff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-height: 450px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input,
select {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 0.5rem;
  border: none;
  background-color: #1e3a8a;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 0.5rem;
}

button:hover {
  background-color: #1c3574;
}

.output-block {
  margin-top: 1rem;
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 4px;
  max-height: 250px;
  overflow-y: auto;
}
</style>

