<!--
Component for handling display/download of job results.
-->
<template>
  <div class="job-results">
   <p>{{ results }} </p>
   <summary-table></summary-table>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

import SummaryTable from "@/components/jobs/data/SummaryTable.vue";

import { System } from "@/types/System";

import * as Jobs from "@/api/jobs";

Vue.component("summary-table", SummaryTable);
@Component
export default class JobResults extends Vue {
  @Prop() jobId!: string;
  @Prop() system!: System;
  loading!: boolean;
  results!: Array<Record<string, any>>;

  created() {
    this.loadResults();
  }
  data() {
    return {
      results: {},
      loading: true
    };
  }
  async loadResults(){
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getResults(token, this.jobId)
    if (response.ok) {
      this.results = await response.json();
      this.loading = false;
    }else {
      console.log("Couldn't load results");
    }
  }
}
</script>
