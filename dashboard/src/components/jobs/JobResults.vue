<!--
Component for handling display/download of job results.
-->
<template>
  <div v-if="job">
    <div v-if="results">
      <div v-if="jobStatus == 'complete'" class="job-results">
        <h2 class="monthly-summary">Monthly Summary</h2>
        <div v-if="summaryData">
          <summary-table :tableData="summaryData"></summary-table>
        </div>
        <h2 class="data-summary">Results and Measurements</h2>
        <p>
          Below is a table of the results of this calculation and user uploaded
          measurements.
          <timeseries-table
            :job="job"
            :resultObjects="results"
            :dataObjects="job.data_objects"
          />
        </p>
        <h2 class="timeseries-header">Timeseries Results</h2>
        <div v-if="results">
          <custom-plot :resultObjects="results" :job="job" />
        </div>
      </div>
      <div v-else>
        Errors occured while processing the calculation.
        <ul v-if="errors">
          <li
            v-for="(error, errno) in errors"
            :key="errno"
            class="warning-text"
          >
            {{ error.error.details }}
          </li>
        </ul>
      </div>
    </div>
    <div v-else>
      <template v-if="jobStatus == 'queued'">
        The calculation is queued and waiting for processing.
      </template>
      <template v-else-if="jobStatus == 'running'">
        The calculation is running and will be ready soon.
      </template>
      <template v-else-if="jobStatus == 'complete'">
        Calculation is complete. Results are loading.
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

import CustomResultPlot from "@/components/jobs/CustomResultPlots.vue";
import SummaryTable from "@/components/jobs/data/SummaryTable.vue";
import TimeseriesPlot from "@/components/jobs/data/Timeseries.vue";
import TimeseriesTable from "@/components/jobs/data/TimeseriesResultsTable.vue";

import { System } from "@/types/System";

import * as Jobs from "@/api/jobs";
import downloadFile from "@/utils/downloadFile";

Vue.component("summary-table", SummaryTable);
Vue.component("timeseries-plot", TimeseriesPlot);
Vue.component("custom-plot", CustomResultPlot);
Vue.component("timeseries-table", TimeseriesTable);

@Component
export default class JobResults extends Vue {
  @Prop() job!: Record<string, any>;
  @Prop() system!: System;
  loading!: boolean;
  selected!: string;
  results!: Array<Record<string, any>>;
  timeseriesData!: any;
  summaryData!: Record<string, any>;
  errors!: Record<string, Record<string, any>>;

  // for tracking the setTimeout callback used for reloading the job
  timeout!: any;

  activated() {
    if (this.jobStatus == "complete") {
      if (!this.results) {
        this.initializeResults();
      }
    } else {
      this.pollUntilComplete();
    }
  }
  deactivated() {
    clearTimeout(this.timeout);
  }
  async pollUntilComplete() {
    const token = await this.$auth.getTokenSilently();
    this.awaitCompletion(token);
  }
  async awaitCompletion(token: string) {
    // fetch the job status until we find something meaningful to report.
    const statusRequest = await Jobs.jobStatus(
      token,
      this.job.object_id
    ).then(response => response.json());
    const jobStatus = statusRequest.status;
    if (jobStatus != this.jobStatus) {
      // Emit an event to reload the job when the status has changed so that
      // JobHandler can react accordingly.
      this.$emit("reload-job");
    }
    if (jobStatus == "complete" || jobStatus == "error") {
      // load results when complete
      this.initializeResults();
    } else {
      // Wait 1 second and poll for status update
      this.timeout = setTimeout(this.awaitCompletion.bind(this, token), 1000);
    }
  }
  initializeResults() {
    this.loadResults().then(() => {
      if (this.jobStatus == "complete") {
        this.loadSummaryResults();
      } else {
        this.loadErrorResults();
      }
    });
  }
  data() {
    return {
      results: null,
      loading: true,
      selected: "",
      timeseriesData: null,
      summaryData: {},
      errors: {}
    };
  }
  get labelledSummaryResults() {
    const summaryData = {};
    if (this.results.length) {
      this.results.forEach((result: Record<string, any>) => {
        if (
          !result.definition.type.includes("summary") &&
          !result.definition.type.includes("vs")
        ) {
          return;
        }
        // @ts-expect-error
        summaryData[result.definition.type] = result.object_id;
      });
      return summaryData;
    } else {
      return null;
    }
  }
  get timeseriesResults() {
    return this.results.filter((result: Record<string, any>) => {
      return !(
        result.definition.type.includes("summary") ||
        result.definition.type.includes("vs")
      );
    });
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
  async loadErrorResultsData(dataId: string) {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getSingleResult(
      token,
      this.jobId,
      dataId
    ).then(response => response.json());
    return response;
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
  get jobTimezone() {
    return this.job.definition.parameters.time_parameters.timezone;
  }
  loadSummaryResults() {
    // Load summary data all at once to display all tables
    for (const summaryType in this.labelledSummaryResults) {
      // @ts-expect-error
      const object_id = this.labelledSummaryResults[summaryType];
      this.loadResultData(object_id).then(data => {
        this.$set(this.summaryData, summaryType, data);
      });
    }
  }
  loadErrorResults() {
    const errorResults = this.results.filter((result: Record<string, any>) => {
      return result.definition.type == "error message";
    });
    for (const result of errorResults) {
      this.loadErrorResultsData(result.object_id).then(data => {
        this.$set(this.errors, result.object_id, data);
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
