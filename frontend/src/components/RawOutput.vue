<template>
  <div v-if="loading" class="d-flex justify-content-center">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>  
  <div v-else>
    <h2 class="my-4">PMC Output</h2>
    <i>{{ (new Date(status.time)).toLocaleString() }}</i>
    <pre>{{ status.output }}</pre>
  </div>
</template>

<script>

import axios from "axios";

export default {
  name: "RawOuput",
  setup() {
  },
  data() {
    return {
      status: {},
      loading: true
    }
  },
  mounted(){
    this.refresh()
  },
  methods: {
    refresh() {
      axios.get("/api/raw_output")
      .then(response => {
        this.status = response.data
        this.loading = false
      })
    },
  }
};
</script>

<style scoped>
/* Optional: You can add additional custom styles if needed */
</style>