<!--
Component for handling display/download of job results.
-->
<template>
  <div v-if="job">
    <div v-if="results" class="job-results">
      <div v-for="(label, id) in labelledSummaryResults" :key="id">
        <h2 class="summary-header">{{ label }}</h2>
        Download:
        <button @click="downloadData('text/csv', label, id)">CSV</button>
        <button
          @click="downloadData('application/vnd.apache.arrow.file', label, id)"
        >
          Apache Arrow
        </button>

        <summary-table
          v-if="loadedSummaryData.includes(id)"
          :tableData="summaryData[id]"
        ></summary-table>
      </div>
      <h2 class="timeseries-header">Timeseries Results</h2>
      <p>Select a timeseries result below to view a plot of the data</p>
      <select v-model="selected" @change="loadTimeseriesData">
        <option value="">Select a timeseries result</option>
        <option
          v-for="(label, id) in labelledTimeseriesResults"
          :key="id"
          :value="id"
        >
          {{ label }}
        </option>
      </select>
      <template v-if="timeseriesData && selected">
        <timeseries-plot
          @download-timeseries="downloadTimeseries"
          :timeseriesData="timeseriesData"
          :title="labelledTimeseriesResults[selected]"
        ></timeseries-plot>
      </template>
    </div>
    <div v-else>
      <template v-if="jobStatus == 'queued'">
        The calculation is queued and waiting for processing.
      </template>
      <template v-else-if="jobStatus == 'running'">
        The calculation is running and will be ready soon.
      </template>
      <template v-else>
        Calculation has not been submitted.
      </template>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { Table } from "apache-arrow";

import SummaryTable from "@/components/jobs/data/SummaryTable.vue";
import TimeseriesPlot from "@/components/jobs/data/Timeseries.vue";

import { System } from "@/types/System";

import * as Jobs from "@/api/jobs";
import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";
import downloadFile from "@/utils/downloadFile";

Vue.component("summary-table", SummaryTable);
Vue.component("timeseries-plot", TimeseriesPlot);
@Component
export default class JobResults extends Vue {
  @Prop() job!: Record<string, any>;
  @Prop() system!: System;
  loading!: boolean;
  selected!: string;
  results!: Array<Record<string, any>>;
  timeseriesData!: any;
  summaryData!: Record<string, any>;
  loadedSummaryData!: Array<string>;

  // for tracking the setTimeout callback used for reloading the job
  timeout!: any;

  activated() {
    if (this.jobStatus == "complete") {
      if (!this.results) {
        this.initializeResults();
      }
    } else {
      this.awaitCompletion();
    }
  }
  deactivated() {
    clearTimeout(this.timeout);
  }
  awaitCompletion() {
    // emit an event to fetch the job and check the new status
    this.$emit("reload-job");
    if (this.jobStatus == "complete") {
      this.initializeResults();
    } else {
      // If the job was not complete, check for
      this.timeout = setTimeout(this.awaitCompletion, 1000);
    }
  }
  initializeResults() {
    this.loadResults().then(() => {
      this.loadSummaryResults();
    });
  }
  data() {
    return {
      results: null,
      loading: true,
      selected: "",
      timeseriesData: null,
      summaryData: {},
      loadedSummaryData: []
    };
  }
  get labelledSummaryResults() {
    const labelled = {};
    if (this.results.length) {
      this.results.forEach((result: Record<string, any>) => {
        if (!result.definition.type.includes("summary")) {
          return;
        }
        const systemComponent = indexSystemFromSchemaPath(
          this.system,
          result.definition.schema_path
        );
        const label = `${systemComponent.name} ${result.definition.type}`;
        // @ts-expect-error
        labelled[result.object_id] = label;
      });
      return labelled;
    } else {
      return null;
    }
  }
  get labelledTimeseriesResults() {
    const labelled = {};
    if (this.results.length) {
      this.results.forEach((result: Record<string, any>) => {
        if (result.definition.type.includes("summary")) {
          return;
        }
        const systemComponent = indexSystemFromSchemaPath(
          this.system,
          result.definition.schema_path
        );
        const label = `${systemComponent.name} ${result.definition.type}`;
        // @ts-expect-error
        labelled[result.object_id] = label;
      });
      return labelled;
    } else {
      return null;
    }
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
  async loadResultData(dataId: string) {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getSingleResult(
      token,
      this.jobId,
      dataId
    ).then(response => response.arrayBuffer());
    return Table.from([new Uint8Array(response)]);
  }
  async loadTimeseriesData() {
    if (this.selected != "") {
      // Set Table to null to avoid drawing the plot before loaded.
      const timeseriesTable = await this.loadResultData(this.selected);
      this.timeseriesData = timeseriesTable;
    }
  }
  get resultObject() {
    for (let i = 0; i < this.results.length; i++) {
      if (this.results[i].object_id == this.selected) {
        return this.results[i];
      }
    }
    return null;
  }
  get jobId() {
    return this.job.object_id;
  }
  get jobStatus() {
    return this.job.status.status;
  }
  loadSummaryResults() {
    // Load summary data all at once to display all tables
    for (const object_id in this.labelledSummaryResults) {
      this.loadResultData(object_id).then(data => {
        this.summaryData[object_id] = data;
        this.loadedSummaryData.push(object_id);
      });
    }
  }
  async downloadTimeseries(contentType: string) {
    this.downloadData(
      contentType,
      // @ts-expect-error
      this.labelledTimeseriesResults[this.selected],
      this.selected
    );
  }
  async downloadData(contentType: string, label: string, dataId: string) {
    const token = await this.$auth.getTokenSilently();
    const fileContents = await Jobs.getSingleResult(
      token,
      this.jobId,
      dataId,
      contentType
    ).then(response => response.blob());

    const filenameLabel = label.replace(/\s/g, "_");
    let filename = `${filenameLabel}.arrow`;
    if (contentType.includes("csv")) {
      filename = `${filenameLabel}.csv`;
    }
    downloadFile(filename, fileContents);
  }
}
</script>
<style></style>
