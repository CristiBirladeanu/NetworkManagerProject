<template>
  <div class="interface-config">
    <h3>Configurare Interfață (show run / show ip)</h3>

    <form @submit.prevent="fetchConfig">
      <select v-model="selectedDevice" @change="fillForm">
        <option disabled value="">Selectează un router</option>
        <option v-for="device in devices" :key="device.ip_address" :value="device.hostname">
          {{ device.hostname }}
        </option>
      </select>

      <input v-model="form.ip" placeholder="IP router" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />

      <button type="button" class="action-btn" @click="loadInterfaces">Încarcă interfețe</button>

      <select v-model="form.interface" required>
        <option disabled value="">Selectează o interfață</option>
        <option v-for="iface in interfaces" :key="iface" :value="iface">{{ iface }}</option>
      </select>

      <button type="submit" class="submit-btn">Vezi Configurație</button>
    </form>

    <div v-if="output.interface">
      <h4>Interfață: {{ output.interface }}</h4>
      <p><strong>Status:</strong> {{ output.status }}</p>
      <p><strong>IP:</strong> {{ output.ip }}</p>

      <h5>show ip interface {{ output.interface }}</h5>
      <pre>{{ output.info }}</pre>

      <h5>show run interface {{ output.interface }}</h5>
      <pre>{{ output.config }}</pre>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'InterfaceConfig',
  props: ['devices'],
  data() {
    return {
      form: {
        ip: '',
        username: '',
        password: '',
        interface: ''
      },
      selectedDevice: '',
      interfaces: [],
      output: {},
      error: ''
    }
  },
  methods: {
    fillForm() {
      const selected = this.devices.find(d => d.hostname === this.selectedDevice)
      if (selected) {
        this.form.ip = selected.ip_address
        this.form.username = selected.username
        this.form.password = selected.password
      }
    },
    async loadInterfaces() {
      this.error = ''
      this.interfaces = []
      try {
        const response = await axios.post('http://localhost:8000/interfaces_list', {
          ip: this.form.ip,
          username: this.form.username,
          password: this.form.password
        })
        if (Array.isArray(response.data)) {
          this.interfaces = response.data
        } else {
          this.error = 'Răspuns invalid de la server.'
        }
      } catch (err) {
        this.error = 'Eroare la încărcarea interfețelor: ' + err.message
      }
    },
    async fetchConfig() {
      this.error = ''
      this.output = {}
      try {
        const response = await axios.post('http://localhost:8000/interface_config', {
          ip: this.form.ip,
          username: this.form.username,
          password: this.form.password,
          interface: this.form.interface
        })
        this.output = response.data
      } catch (err) {
        this.error = 'Eroare la extragerea configurației: ' + err.message
      }
    }
  }
}
</script>

<style scoped>
.interface-config {
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
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  margin-right: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn {
  background-color: #1e3a8a;
  color: white;
}

.action-btn {
  background-color: #1e3a8a;
  color: white;
}

.error {
  color: red;
  margin-top: 1rem;
}

pre {
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 4px;
  overflow-x: auto;
}
</style>

