<template>
  <div class="ospf-configure-form">
    <h3>Configurează OSPF</h3>

    <form @submit.prevent="sendOspfConfig">
      <select v-model="selectedDevice" @change="fillForm">
        <option disabled value="">Selectează un router</option>
        <option v-for="device in devices" :key="device.ip_address" :value="device.hostname">
          {{ device.hostname }}
        </option>
      </select>

      <input v-model="form.ip" placeholder="IP router" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />
      <input v-model.number="form.process_id" placeholder="Process ID (ex: 1)" required />

      <button type="button" class="action-btn" @click="autoDetectNetworks">Detectează rețele</button>
      <input v-model="form.mgmt_network" placeholder="Rețea management (opțional, ex: 192.168.100.0/24)" />

      <div
        v-for="(network, index) in form.networks"
        :key="index"
        class="network-group"
      >
        <input v-model="network.ip" placeholder="Network IP (ex: 10.0.0.0)" required />
        <input v-model="network.wildcard" placeholder="Wildcard (ex: 0.0.0.255)" required />
        <input v-model.number="network.area" placeholder="Area (ex: 0)" required />
        <button type="button" class="danger-btn" @click="removeNetwork(index)" v-if="form.networks.length > 1">
          Șterge rețea
        </button>
      </div>

      <button type="button" class="action-btn" @click="addNetwork">Adaugă rețea</button>
      <button type="submit" class="submit-btn">Trimite configurare</button>
    </form>

    <div class="ospf-reset">
      <button class="reset-btn" @click="resetOspf('restart')">Resetare OSPF (restart)</button>
      <button class="danger-btn" @click="resetOspf('remove')">Șterge OSPF (remove)</button>
    </div>

    <div v-if="output">
      <h4>Rezultat:</h4>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'OSPFConfigureForm',
  props: ['devices'],
  data() {
    return {
      form: {
        ip: '',
        username: '',
        password: '',
        process_id: 1,
        mgmt_network: '',
        networks: [
          { ip: '', wildcard: '', area: 0 }
        ]
      },
      output: '',
      selectedDevice: ''
    }
  },
  methods: {
    addNetwork() {
      this.form.networks.push({ ip: '', wildcard: '', area: 0 })
    },
    removeNetwork(index) {
      this.form.networks.splice(index, 1)
    },
    fillForm() {
      const selected = this.devices.find(d => d.hostname === this.selectedDevice)
      if (selected) {
        this.form.ip = selected.ip_address
        this.form.username = selected.username
        this.form.password = selected.password
      }
    },
    async sendOspfConfig() {
      try {
        const payload = {
          ip: this.form.ip,
          username: this.form.username,
          password: this.form.password,
          process_id: this.form.process_id,
          networks: this.form.networks
        }
        const response = await axios.post('http://localhost:8000/ospf_configure', payload)
        this.output = response.data.output
      } catch (error) {
        this.output = 'Eroare: ' + error.message
      }
    },
    async resetOspf(mode) {
      try {
        const payload = {
          ip: this.form.ip,
          username: this.form.username,
          password: this.form.password,
          process_id: this.form.process_id,
          mode: mode
        }
        const response = await axios.post('http://localhost:8000/ospf_reset', payload)
        this.output = response.data.output
      } catch (error) {
        this.output = 'Eroare la resetare: ' + error.message
      }
    },
    async autoDetectNetworks() {
      try {
        const payload = {
          ip: this.form.ip,
          username: this.form.username,
          password: this.form.password,
          mgmt_network: this.form.mgmt_network || undefined
        }
        const response = await axios.post('http://localhost:8000/ospf_autodiscover', payload)
        this.form.networks = response.data.map(net => ({
          ip: net.ip,
          wildcard: net.wildcard,
          area: net.area
        }))
      } catch (error) {
        this.output = 'Eroare la detectare rețele: ' + error.message
      }
    }
  }
}
</script>

<style scoped>
.connect-form {
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

.reset-btn {
  background-color: #4b5563;
  color: white;
}

.danger-btn {
  background-color: #c0392b;
  color: white;
}

.ospf-reset {
  margin-top: 1rem;
}
</style>

