<!--
Component for handling display/download of job results.
-->
<template>
  <div class="job-results">
    Selected:
    <input type="radio" v-model="selected" value="summary" />
    summary
    <input type="radio" v-model="selected" value="data" />
    data
    <summary-table v-if="selected == 'summary'"></summary-table>
    <timeseries-plot
      v-if="selected == 'data'"
      :tableData="tableData"
    ></timeseries-plot>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { Table } from "apache-arrow";

import SummaryTable from "@/components/jobs/data/SummaryTable.vue";
import TimeseriesPlot from "@/components/jobs/data/Timeseries.vue";

import { System } from "@/types/System";

import * as Jobs from "@/api/jobs";

Vue.component("summary-table", SummaryTable);
Vue.component("timeseries-plot", TimeseriesPlot);
@Component
export default class JobResults extends Vue {
  @Prop() jobId!: string;
  @Prop() system!: System;
  loading!: boolean;
  selected!: string;
  results!: Array<Record<string, any>>;
  tableData!: any;

  created() {
    this.loadResults();
    this.loadDataResult("bah");
  }
  data() {
    return {
      results: {},
      loading: true,
      selected: "summary"
    };
  }
  async loadResults() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getResults(token, this.jobId);
    if (response.ok) {
      this.results = await response.json();
      this.loading = false;
    } else {
      console.log("Couldn't load results");
    }
  }
  async loadDataResult(dataId: string) {
    const jobId = "eb7f3708-601e-11eb-8c35-0242ac110002";
    dataId = "eb7f4faa-601e-11eb-8c35-0242ac110002";
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getData(token, jobId, dataId).then(response =>
      response.arrayBuffer()
    );
    this.tableData = Table.from([new Uint8Array(response)]);
  }
}
</script>
