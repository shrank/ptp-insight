<template>
      <div class="col-auto">
        <label for="configSelect" class="form-label">Select PTP Config:</label>
      </div>
      <div class="col-auto">
        <select
          id="configSelect"
          class="form-select"
          v-model="selectedConfig"
          :disabled="configs.length === 0"
        >
          <option value="" disabled>Select a configuration</option>
          <option
            v-for="config in configs"
            :key="config[1]"
            :value="config[1]"
          >
            {{ config[0] }}
          </option>
        </select>
      </div>
      <div class="col-auto">
        <button
          class="btn btn-primary"
          @click="applyConfig"
          :disabled="!selectedConfig"
        >
          Apply
        </button>
      </div>
      <div class="col-auto">
        <div v-if="message" class="mt-3 alert alert-info">
          {{ message }}
        </div>
      </div>
</template>

<script>

import axios from "axios";

export default {
  name: "PtpConfig",
  setup() {
  },
  data() {
    return {
      configs: [],
      selectedConfig: '',
      message: ''
    }
  },
  mounted(){
    axios.get('/api/configs')
    .then(response => {
      this.configs = response.data.available
      this.selectedConfig = response.data.current
      console.log(this.selectedConfig)
    })
    .catch (err => {
      this.message = 'Failed to load configurations.'
      console.error(err)
    })
  },
  methods: {
    applyConfig() {
      axios.post('/api/config', { new_config: this.selectedConfig })
      .then((response)=> {
        this.message = response.data.message
      })
      .catch (err => {
        this.message = 'Error applying configuration.';
        console.error(err);
      })
    }
  }
}
</script>
