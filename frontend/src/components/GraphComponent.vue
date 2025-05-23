<template>
  <div class="content-block">
      <h5 @click="open=(open===false)">{{title}}</h5>
      <div v-if="open">
        <slot></slot>
        <TimeSeriesChart :metric="metric" :refresh="refresh" :timeframe="timeframe" :db_filter="db_filter" style="height: 300px;   margin-bottom: 50px;"></TimeSeriesChart>
      </div>
  </div>
</template>

<script>

import TimeSeriesChart from "./TimeSeriesChart.vue";


export default {
  name: "GraphComponent",
  components: {
    TimeSeriesChart
  },
  setup() {
  },
  props:{
    refresh: Number,
    title: String,
    metric: String,
    timeframe: Number,
    db_filter: String
  },
  data() {
    return {
      open: false
    }
  },
};
</script>

<style scoped>
/* Optional: You can add additional custom styles if needed */
</style>