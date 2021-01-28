<!--
Component for handling display/download of job results.
-->
<template>
  <div v-if="results" class="job-results">
    <div v-for="(label, id) in labelledResults" :key="id">
      <input
        type="radio"
        @change="loadResultData"
        v-model="selected"
        :value="id"
      />
      {{ label }}
    </div>
    <!--<pre>
      {{ results }}
    </pre>-->
    <template v-if="tableData && resultObject">
      <summary-table
        v-if="resultObject.definition.type.includes('summary')"
        :tableData="tableData"
      ></summary-table>
      <timeseries-plot v-else :tableData="tableData"></timeseries-plot>
    </template>
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
    this.loadResults().then(() => {
      this.selectSummary();
      this.loadResultData();
    });
  }
  data() {
    return {
      results: null,
      loading: true,
      selected: "",
      tableData: null
    };
  }
  get labelledResults() {
    const labelled = {};
    if (this.results.length) {
      this.results.forEach((result: Record<string, any>) => {
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
  async loadResultData() {
    // Set Table to null to avoid drawing the plot before loaded.
    this.tableData = null;
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.getSingleResult(
      token,
      this.jobId,
      this.selected
    ).then(response => response.arrayBuffer());
    this.tableData = Table.from([new Uint8Array(response)]);
  }
  get resultObject() {
    for (let i = 0; i < this.results.length; i++) {
      if (this.results[i].object_id == this.selected) {
        return this.results[i];
      }
    }
    return null;
  }
  selectSummary() {
    this.selected = this.results[0].object_id;
    for (let i = 0; i < this.results.length; i++) {
      if (this.results[i].definition.type.includes("summary")) {
        this.selected = this.results[i].object_id;
      }
    }
  }
}
</script>
