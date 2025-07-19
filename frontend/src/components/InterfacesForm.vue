<template>
  <div class="interface-form">
    <h3>Status interfețe router</h3>

    <form @submit.prevent="getInterfaces">
      <select v-model="selectedDevice" @change="fillForm">
        <option disabled value="">Selectează un router</option>
        <option v-for="device in devices" :key="device.ip_address" :value="device.hostname">
          {{ device.hostname }}
        </option>
      </select>

      <input v-model="form.ip" placeholder="IP router" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />
      <button type="submit">Afișează interfețe</button>
    </form>

    <div v-if="output" class="result">
      <h4>Rezultat:</h4>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'InterfacesForm',
  props: ['devices'],
  data() {
    return {
      form: {
        ip: '',
        username: '',
        password: ''
      },
      output: '',
      selectedDevice: ''
    }
  },
  methods: {
    async getInterfaces() {
      try {
        const response = await axios.post('http://localhost:8000/interfaces', this.form)
        this.output = response.data.output
      } catch (error) {
        this.output = 'Eroare: ' + error.message
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
.interface-form {
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

input, select {
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
}

button:hover {
  background-color: #1c3574;
}

.result {
  margin-top: 1rem;
}
</style>

