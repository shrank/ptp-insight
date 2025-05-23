<template>
  <!-- Sidebar (Navigation Bar) -->
  <div id="sidebar" v-if="show_menu">
    <nav class="nav flex-column">
      <a @click="change_page('')" class="nav-link active">Overview</a>
        <hr>
        <a @click="change_page('raw')"  class="nav-link">Raw Output</a>
        <hr>
        <a @click="change_page('log')"  class="nav-link">Logs</a>
    </nav>
  </div>
  <!-- Overlay (used to hide content when the sidebar is active) -->
  <div id="overlay" v-if="show_menu2" @click="show_menu=false"></div>

  <div class="menu-button">
      <!-- Hamburger Menu Button -->
      <button id="menu-toggle" class="btn btn-primary mt-3" @click="show_menu=(show_menu == false)">☰ Menu</button>
  </div>

  <div class="container-fluid">
    <div class="row">
        <!-- Main Content Area -->
        <div class="col-12 mt-3 p-3" id="main-content">
        
        <RawOutput v-if="page=='raw'" ></RawOutput>
        <LogViewer v-if="page=='log'" ></LogViewer>
        <div v-else>
          <PtpConfig></PtpConfig>
          <StatusOverview  :config="config" :refresh="cnt" :db_filter="filter"></StatusOverview>
          <GraphComponent title="Incoming Time" metric="time_status_np_ingress_time" :refresh="cnt" :timeframe="timeframe" :db_filter="filter">
          The nanosecond timestamp as received from the master clock. In general, this should continually and liniarely increase over time.
          </GraphComponent>
          <GraphComponent title="RMS" metric="clock_stats_rms" :refresh="cnt" :timeframe="timeframe" :db_filter="filter">
            Root Mean Square of time offset from leader clock in nanoseconds.
          </GraphComponent>
          <GraphComponent title="Delay" metric="clock_stats_delay" :refresh="cnt" :timeframe="timeframe" :db_filter="filter">
          The delay to the master or peer clock as calculated by the delay mechanism. The path correction delay as reported by transparent clocks(switches) is already accounted for(removed from) this value  
          </GraphComponent>
          <GraphComponent title="Frequency Deviation" metric="clock_stats_freq_deviation" :refresh="cnt" :timeframe="timeframe" :db_filter="filter">
            The deviation in frequency adjustment of the clock in parts per billion(ppb)
          </GraphComponent>
          <GraphComponent title="Network Delay" metric="network_delay" :refresh="cnt" :timeframe="timeframe" :db_filter="filter">
            Network correction delay as imposed by tranparent bridges(siwtches) on the network. This should be around 1000-2000ns per switch hop
          </GraphComponent>
        </div>
        </div>
    </div>
</div>

</template>

<script>
import axios from "axios";
import PtpConfig from "./components/PtpConfig.vue";
import StatusOverview from "./components/StatusOverview.vue";
import RawOutput from "./components/RawOutput.vue";
import GraphComponent from "./components/GraphComponent.vue";
import LogViewer from "./components/LogViewer.vue";

export default {
  name: 'App',
  components: {
    StatusOverview,
    RawOutput,
    GraphComponent,
    PtpConfig,
    LogViewer
  },
  data() {
    return  {
      show_menu: false,
      page: "",
      config: {},
      cnt: 0,
      timeframe: 300,
      filter: ""
    }
  },
  mounted(){
    this.refresh_config()
    setInterval(() => {
      axios.get("/api/now")
      .then(response => {
        this.cnt = response.data.now
      })
    }, 5000)
  },
  methods: {
    change_page(page) {
      this.show_menu = false
      this.page = page
      console.log(page)
    },
    refresh_config() {
      axios.get("/api/serverconfig")
      .then(response => {
        this.config = response.data
        this.filter= `{db="${this.config.influx_database}",reporter_id="${this.config.reporter_id}"}`
      })
    }
  }
}
</script>

<style>
.menu-button {
  position: absolute;
  right: 12px;
}

.menu-button button {
  height: 60px;
}

</style>
