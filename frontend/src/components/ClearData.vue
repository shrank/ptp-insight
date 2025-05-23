<template>
  <div class="col-auto">
    <button
      class="btn btn-primary"
      @click="clear"
    >
      Clear All Data
    </button>
  </div>
</template>

<script>

import axios from "axios";

export default {
  name: "ClearData",
  setup() {
  },
  props: {
    db_filter: String
  },
  data() {
    return {
      configs: [],
      selectedConfig: '',
      message: ''
    }
  },
  methods: {
    clear() {
      const r = confirm("delete all ptp-insight data for this reporter_id?")
      if(r===false) {
        return
      }
      const metrics = ["time_status_np_ingress_time", "clock_stats_rms", "clock_stats_delay", "clock_stats_freq_deviation", "network_delay","time_status_np_gm_present", "time_status_np_ingress_time"]
      for (let m of metrics) {
        axios.get('/api/v1/admin/tsdb/delete_series?match[]=' + m + this.db_filter)
      }
    }
  }
}
</script>
