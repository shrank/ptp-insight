<template>
  <div v-if="loading" class="d-flex justify-content-center">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>  
  <div v-else>
    <LineChart :data="chartData" :options="chartOptions" updateMode="resize"/>
    
    <!-- Display Min, Max, and Avg values below the graph -->
    <div v-if="timeseriesDataValues.length">
      <div class="stats-container">
        <div><strong>Min:</strong> {{ minValue }}</div>
        <div><strong>Max:</strong> {{ maxValue }}</div>
        <div><strong>Avg:</strong> {{ avgValue }}</div>
        <div><strong>Spread:</strong> {{ maxValue - minValue }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { Line } from "vue-chartjs";
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, TimeScale, LinearScale } from 'chart.js';
import axios from "axios";
import 'chartjs-adapter-luxon';

// Register necessary components with Chart.js
ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, TimeScale, LinearScale);

export default {
  name: "TimeSeriesChart",
  components: {
    LineChart: Line
  },
  props: {
    metric: String,
    refresh: Number,
    timeframe: Number,
    db_filter: String
  },
  data(){
    return {
      chartOptions:{
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'linear',
            title: {
              display: false,
              text: "Time passed"
            },
            min: -300,
            max: 0,
            ticks: {
              callback: value => {
                // Format time dynamically
                const seconds = value * -1
                if (seconds < 60) {
                  return `${seconds}s`
                } else if (seconds < 3600) {
                  return `${(seconds / 60).toFixed(1)}m`
                } else {
                  return `${(seconds / 3600).toFixed(2)}h`
                }
              }
            }
          }
        //   y: {
        //     title: {
        //       display: true,
        //       text: "Value"
        //     }
        //   }
        // },
        },
        plugins: {
          legend: {
            display: false
          }
        }
      },
      loading: true,
      timeseriesDataValues:[],
      timeseriesDataLabels:[]
    }
  },
  computed: {
      chartData() {
        return {
          labels: this.timeseriesDataLabels,   // Timestamps
          datasets: [   // Data for the line chart
          {
              // label: "Time Series Data", 
              data: this.timeseriesDataValues, 
              fill: false, 
              borderColor: 'rgba(75, 192, 192, 1)', 
              tension: 0.1
            }
          ],
        }
      },
      // Calculate min, max, and avg values
      minValue(){
      return this.timeseriesDataValues.length
        ? Math.min(...this.timeseriesDataValues)
        : null;
    },
    maxValue(){
      return this.timeseriesDataValues.length
        ? Math.max(...this.timeseriesDataValues)
        : null;
    },
    avgValue(){
      if (this.timeseriesDataValues.length) {
        const sum = this.timeseriesDataValues.reduce((acc, item) => acc + item, 0);
        return (sum / this.timeseriesDataValues.length).toFixed(2); // 2 decimals
      }
      return null;
    }
  },
  watch:{
    refresh(){
      this.refresh_data()
    }
  },
  mounted(){
    this.refresh_data()
  },
  methods: {
    refresh_data() {
      const time = this.timeframe
      this.chartOptions.scales.min= time * -1
      let step = Math.floor(this.timeframe / 1000)
      if(step < 1) {
        step = 1
      }
      let url = `/api/v1/query_range?query=max(${this.metric}${this.db_filter})&start=-${time}s&step=${step}s`
      axios.get(url)
      .then(response => {
        if(response.data.data.result.length <1) {
          console.log("No Data")
          this.loading = false
          return
        }
        const timeseriesData = response.data.data.result[0].values
        if (timeseriesData.length > 0) {
          this.timeseriesDataValues = timeseriesData.map(item => parseInt(item[1])),
          this.timeseriesDataLabels = timeseriesData.map(item => item[0] - this.refresh)
       }
       this.loading = false
      })
    }
  }
};
</script>

<style scoped>
/* Style the container for stats */
.stats-container {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  font-weight: bold;
}

.stats-container div {
  padding: 5px;
}
</style>
