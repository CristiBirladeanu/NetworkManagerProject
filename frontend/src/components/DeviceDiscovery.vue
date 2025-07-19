<template>
  <div class="device-discovery">
    <h3>Descoperă routere din topologie</h3>

    <form @submit.prevent="discoverDevices">
      <input v-model="form.seed_ip" placeholder="IP seed (ex: 192.168.100.2)" required />
      <input v-model="form.username" placeholder="Username SSH" required />
      <input v-model="form.password" type="password" placeholder="Password SSH" required />
      <button type="submit">Descoperă</button>
    </form>

    <div v-if="loading" class="loading">Descoperire în curs...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="devices.length > 0 && !loading && !error" class="success">
      <p>Descoperire reușită: {{ devices.length }} deviceuri găsite.</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'DeviceDiscovery',
  emits: ['discovered'],
  setup(_, { emit }) {
    const form = ref({
      seed_ip: '',
      username: '',
      password: ''
    })

    const devices = ref([])
    const error = ref('')
    const loading = ref(false)

    async function discoverDevices() {
      error.value = ''
      devices.value = []
      loading.value = true

      try {
        const response = await axios.get('http://localhost:8000/devices', {
          params: {
            seed_ip: form.value.seed_ip,
            username: form.value.username,
            password: form.value.password
          }
        })
        devices.value = response.data
        emit('discovered', devices.value)
      } catch (err) {
        error.value = 'Eroare la descoperirea deviceurilor: ' + err.message
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      devices,
      error,
      loading,
      discoverDevices
    }
  }
}
</script>

<style scoped>
.device-discovery {
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

input {
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

.loading {
  color: #1e3a8a;
  font-weight: bold;
  margin-top: 1rem;
}

.error {
  color: red;
  margin-top: 1rem;
}

.success {
  color: green;
  margin-top: 1rem;
}
</style>

