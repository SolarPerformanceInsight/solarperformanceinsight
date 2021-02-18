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
      <!--
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
          :tz="jobTimezone"
        ></timeseries-plot>
      </template>
      -->
      <div v-if="results">
        <!-- <h2 class="timeseries-header">Custom Timeseries Plots</h2>
        <p>
          Select timeseries data and click
          <i>Add to plot</i>
          to create a list of data to plot. Then click
          <i>Create Plot</i>
          to create a plot of the selected data.
        </p>
        -->
        <custom-plot :resultObjects="results" :job="job" />
      </div>
    </div>
    <div v-else>
      {{ jobStatus }}
      <template v-if="jobStatus == 'queued'">
        The calculation is queued and waiting for processing.
      </template>
      <template v-else-if="jobStatus == 'running'">
        The calculation is running and will be ready soon.
      </template>
      <template v-else-if="jobStatus == 'error'">
        An error occured while processing the calculation.
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
import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";
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
  loadedSummaryData!: Array<string>;

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
    if (jobStatus == "complete") {
      // load results when complete
      this.initializeResults();
    } else if (jobStatus == "error") {
      // discontinue polling
      return;
    } else {
      // Wait 1 second and poll for status update
      this.timeout = setTimeout(this.awaitCompletion.bind(this, token), 1000);
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
      loadedSummaryData: [],
      errors: null
    };
  }
  get labelledSummaryResults() {
    const comparisons = {};
    const summaries = {};
    if (this.results.length) {
      this.results.forEach((result: Record<string, any>) => {
        if (
          !result.definition.type.includes("summary") &&
          !result.definition.type.includes("vs")
        ) {
          return;
        }
        const systemComponent = indexSystemFromSchemaPath(
          this.system,
          result.definition.schema_path
        );
        const label = `${systemComponent.name} ${result.definition.type}`;
        if (label.includes(" vs ")) {
          // @ts-expect-error
          comparisons[result.object_id] = label;
        } else {
          // @ts-expect-error
          summaries[result.object_id] = label;
        }
      });
      return { ...comparisons, ...summaries };
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
        const label = `${systemComponent.name} ${result.definition.type} (${result.definition.schema_path})`;
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
  get jobTimezone() {
    return this.job.definition.parameters.time_parameters.timezone;
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
