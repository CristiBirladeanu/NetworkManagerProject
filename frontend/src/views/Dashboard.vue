<template>
  <div class="dashboard-view">
    <div class="header">
      <h1>NetManage</h1>
      <p class="subtitle">Network Management and Automation Tool</p>
    </div>

    <div class="dashboard-grid">
      <DeviceDiscovery @discovered="updateDeviceList" />
      <NetworkMap :devices="devices" />
      <ConnectForm :devices="devices" />
      <PingForm :devices="devices" />
      <InterfacesForm :devices="devices" />
      <OSPFConfigureForm :devices="devices" />
      <OSPFStatusPanel :devices="devices" />
      <InterfaceConfig :devices="devices" />
    </div>
    <div class="logs-wrapper">
      <LogsPanel :devices="devices" />
    </div>
  </div>
</template>

<script>
import DeviceDiscovery from '../components/DeviceDiscovery.vue'
import ConnectForm from '../components/ConnectForm.vue'
import PingForm from '../components/PingForm.vue'
import InterfacesForm from '../components/InterfacesForm.vue'
import OSPFConfigureForm from '../components/OSPFConfigureForm.vue'
import OSPFStatusPanel from '../components/OSPFStatusPanel.vue'
import NetworkMap from '../components/NetworkMap.vue'
import LogsPanel from '../components/LogsPanel.vue'
import InterfaceConfig from '../components/InterfaceConfig.vue'

export default {
  name: 'DashboardView',
  components: {
    DeviceDiscovery,
    ConnectForm,
    PingForm,
    InterfacesForm,
    OSPFConfigureForm,
    OSPFStatusPanel,
    InterfaceConfig,
    NetworkMap,
    LogsPanel
  },
  data() {
    return {
      devices: []
    }
  },
  methods: {
    updateDeviceList(list) {
      this.devices = list
    }
  }
}
</script>

<style scoped>
.dashboard-view {
  padding: 2rem;
  background-color: #1e3a8a;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
}

.subtitle {
  font-size: 1.1rem;
  color: #d1d5db;
  margin-top: 0.5rem;
}

.dashboard-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
  align-items: stretch;
}

.dashboard-grid > * {
  flex: 1 1 500px;
  max-width: 600px;
  min-height: 450px;
  background-color: #ffffff;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.logs-wrapper {
  margin-top: 2rem;
  background-color: #ffffff;
  padding: 1rem;
  border-radius: 8px;
  max-width: 95%;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.08);
}
</style>

