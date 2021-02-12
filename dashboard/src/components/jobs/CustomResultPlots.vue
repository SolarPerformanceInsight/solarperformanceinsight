<template>
  <div class="custom-plot-definer" v-if="dataObjects && resultObjects">
    <p> Do the thing</p>
    <!-- Select whether to choose results or data -->
    <select v-model="dataSource">
      <option value="results">Results </option>
      <option value="upload">Uploaded Data</option>
    </select>
    <!-- Select the data or result to add to the plot -->
    <select v-model="selectedObject">
      <option v-for="dataOption of dataOptions" :value="dataOption" :key="dataOption.object_id">
       {{ dataOption.definition.type }} {{ dataOption.definition.schema_path }}
      </option>
    </select>
    <!-- Select the variable to add -->
    <select v-model="selectedVariable">
      <option v-for="variable in variables" :key="variable"> {{ variable }}</option>
    </select>
    <button @click="addToPlot">Add to plot</button><br/>
    <!-- List the data added to the plot -->
    <b>Data to plot:</b>
    <ul>
      <li v-for="(value, dataId) in toPlot" :key="dataId"> {{ dataId }}</li>
    </ul>
    <button @click="createPlot">PLOT THIS!</button>
    <multi-plot v-for="(pd, i) in plotData" :key="i" :timeseriesData="pd" :tz="job.tz">{{i}}</multi-plot>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import MultiTimeseriesPlots from "@/components/jobs/data/MultiTimeSeries.vue";

import * as Jobs from "@/api/jobs"
import { Table } from "apache-arrow";

Vue.component("multi-plot", MultiTimeseriesPlots);

@Component
export default class CustomPlots extends Vue {
  @Prop() job!: Record<string, any>;
  @Prop() resultObjects!: Array<Record<string, any>>;

  // Acutal API data objects to handle
  toPlot!: Record<string, any>;

  // component control properties
  dataSource!: string;
  selectedObject!: Record<string, any>;
  currentData!: any;
  loadingData!: boolean;
  selectedVariable!: string;

  plotData!: Array<Record<string, any>>;

  created() {
    this.selectedObject = this.dataOptions[0];
  }

  data() {
    return {
      dataSource: "results",
      selectedObject: null,
      selectedVariable: "",
      currentData: null,
      loadingData: false,
      toPlot: {},
      plotData: []
    }
  }

  addToPlot() {
    console.log("Adding to plot!");
    const dataId = this.selectedObject.object_id + this.selectedVariable;
    this.$set(
      this.toPlot,
      dataId,
      {
        data: this.currentData.getColumn(this.selectedVariable),
        index: this.currentData.getColumn("time"),
        name: dataId
      }
    )
  }
  removeFromPlot(dataId: string) {
    delete this.toPlot[dataId];
  }
  createPlot() {
    const dataToPlotData: Array<any> = [];
    for (const key in this.toPlot) {
      dataToPlotData.push(this.toPlot[key]);
    }
    this.plotData.push(dataToPlotData);
    this.toPlot = {};
  }
  filteredObjects(toFilter: Array<Record<string, any>>) {
    return toFilter.filter(x => {
      return !(
        x.definition.type.includes(" vs ") ||
        x.definition.type.includes("summarry")
      );
    });
  }
  get dataObjects() {
    return this.job.data_objects;
  }
  get dataOptions() {
    if (this.dataSource == "results") {
      return this.filteredObjects(this.resultObjects);
    } else {
      return this.filteredObjects(this.dataObjects);
    }
  }
  async loadData() {
    let fetchFunc = Jobs.getData;
    if (this.dataSource == "results") {
      fetchFunc = Jobs.getSingleResult;
    }
    const token = await this.$auth.getTokenSilently();
    const response = await fetchFunc(
      token,
      this.job.object_id,
      this.selectedObject.object_id
    ).then(payload => payload.arrayBuffer());
    return Table.from([new Uint8Array(response)]);
  }
  get variables() {
    if (this.currentData) {
      return this.currentData.schema.fields
        .map((x: any) => x.name)
        .filter((y: string) => (y != "time" && y != "month"));
    } else {
      return [];
    }
  }
  @Watch("selectedObject")
  updateData() {
    this.loadingData = true;
    this.loadData().then((data) => {
      this.currentData = data;
      this.loadingData = false;
    })
  }
}
</script>
