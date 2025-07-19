<template>
  <div class="ping-form">
    <h3>Testare ping router → destinație</h3>

    <form @submit.prevent="sendPing">
      <select v-model="selectedDevice" @change="fillForm">
        <option disabled value="">Selectează un router</option>
        <option v-for="device in devices" :key="device.ip_address" :value="device.hostname">
          {{ device.hostname }}
        </option>
      </select>

      <input v-model="form.ip" placeholder="IP router" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />
      <input v-model="form.destination" placeholder="Destinație ping (ex: 10.0.1.10)" required />
      <button type="submit">Trimite ping</button>
    </form>

    <div v-if="output">
      <h4>Rezultat:</h4>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PingForm',
  props: ['devices'],
  data() {
    return {
      form: {
        ip: '',
        username: '',
        password: '',
        destination: ''
      },
      output: '',
      selectedDevice: ''
    }
  },
  methods: {
    async sendPing() {
      try {
        const response = await axios.post('http://localhost:8000/ping', this.form)
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

