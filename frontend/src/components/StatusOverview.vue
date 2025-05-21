<template>
  <div v-if="loading" class="d-flex justify-content-center">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>  
  <div v-else>
    <h2 class="my-4">Status</h2>
    <div v-if="status.gm_present == undefined">
      no data
    </div>
    <table v-else class="table table-bordered table-striped table-hover">
      <tbody>
        <tr>
          <td>Time</td>
          <td>{{ formatDate(status.time) }}</td>
        </tr>
        <tr>
          <td>Status</td>
          <td v-if="status.gm_present == 1"> CONNECTED </td>
          <td v-else> NO MASTER </td>
        </tr>
        <tr>
          <td>Grandmaster</td>
          <td>{{ status.gm_id }}</td>
        </tr>
        <tr>
          <td>Grandmaster IP</td>
          <td>{{ status.gm_ip }}</td>
        </tr>
        <tr>
          <td>Grandmaster MAC</td>
          <td>{{ status.gm_mac }}</td>
        </tr>
        <tr>
          <td>Incoming DSCP Tag</td>
          <td>{{ status.dscp }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

import axios from "axios";

export default {
  name: "StatusOverview",
  setup() {
  },
  props:{
    config: Object,
    refresh: Number

  },
  data() {
    return {
      status: {},
      loading: true
    }
  },
  mounted(){
    this.refresh_data()
  },
  watch:{
    refresh(){
      this.refresh_data()
    }
  },
  methods: {
    refresh_data() {
      //const time = "1h"
      //let url = `/api/v1/query?query=last_over_time(time_status_np_offset[${time}]),last_over_time(time_status_np_ingress_time[${time}]),last_over_time(time_status_np_gm_present[${time}])`
      let url = `/api/v1/query?query=last_over_time(time_status_np_gm_present[10s])`
      axios.get(url)
      .then(response => {
        if(response.data.data.result.length > 0) {
          this.status["gm_present"] = response.data.data.result[0].value[1]
          this.status["gm_id"] = response.data.data.result[0].metric.gm_identity
          this.loading = false
        }
        this.loading = true
      })
      .catch(response => {console.log(response)})
      url = `/api/v1/query?query=last_over_time(time_status_np_ingress_time[10s])`
      axios.get(url)
      .then(response => {
        if(response.data.data.result.length > 0) {
          this.status["time"] = response.data.data.result[0].value[1]
          this.loading = false
        }
      })
      .catch(response => {console.log(response)})
      url = `/api/v1/query?query=last_over_time(network_delay[10s])`
      axios.get(url)
      .then(response => {
        if(response.data.data.result.length > 0) {
          this.status["gm_ip"] = response.data.data.result[0].metric.master_ip
          this.status["gm_mac"] = response.data.data.result[0].metric.master_mac
          this.status["dscp"] = response.data.data.result[0].metric.dscp
          this.loading = false
        } else {
          this.status["gm_ip"] = ""
          this.status["gm_mac"] = ""
          this.status["dscp"] = ""
        }
      })
      .catch(response => {console.log(response)})
    },
    //Format the date for display
    formatDate(ts) {
      const ms = ts / 1000000
      const ns = String(ts % 1000000)

      const date = new Date(ms)

      const day = String(date.getDate()).padStart(2, '0'); // Adds leading zero if needed
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based, so we add 1
      const year = date.getFullYear();
      
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      const milliseconds = String(date.getMilliseconds()).padStart(4, '0'); // 4 digits for milliseconds

      return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}:${milliseconds}.${ns}`;

    }
  }
};
</script>

<style scoped>
/* Optional: You can add additional custom styles if needed */
</style>