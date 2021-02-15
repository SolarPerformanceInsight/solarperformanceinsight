<template>
  <div class="custom-plot-definer" v-if="dataObjects && resultObjects">
    <button @click="createPlot">
      Create Plot
    </button>
    <div v-for="(pd, id) in plotData" :key="id">
      <!-- Select whether to choose results or data -->
      <select v-model="dataSource" @change="selectedObject = dataOptions[0]">
        <option value="results">Results</option>
        <option value="upload">Uploaded Data</option>
      </select>
      <!-- Select the data or result to add to the plot -->
      <select v-model="selectedObject">
        <option
          v-for="dataOption of dataOptions"
          :value="dataOption"
          :key="dataOption.object_id"
        >
          {{ dataOption.definition.type }}
          {{ dataOption.definition.schema_path }}
        </option>
      </select>
      <!-- Select the variable to add -->
      <select v-model="selectedVariable" v-if="selectedObject">
        <option value="">Select A Variable</option>
        <option v-for="variable in variables" :key="variable" :value="variable">
          {{ variableName(variable) }}
        </option>
      </select>
      <button :disabled="!selectedVariable" @click="addToPlot(id)">
        Add to plot
      </button>
      <br />
      <!-- List the data added to the plot -->
      <b>Plot Data:</b>
      <ul>
        <li v-if="Object.keys(plotData[id]).length == 0" class="warning-text">
          No data selected
        </li>
        <li v-for="(value, dataId) in plotData[id]" :key="dataId">
          {{ value.name }}
        </li>
      </ul>
      <multi-plot
        :timeseriesData="pd"
        :tz="timezone"
        :index="id"
        @remove-plot="removePlot"
      />
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import MultiTimeseriesPlots from "@/components/jobs/data/MultiTimeSeries.vue";

import * as Jobs from "@/api/jobs";
import { Table } from "apache-arrow";
import { getIndex } from "@/utils/fieldIndex";
import { getVariableDisplayName } from "@/utils/displayNames";
import { getVariableUnits } from "@/utils/units";

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

  plotData!: Record<number, any>;

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
      plotData: {}
    };
  }
  addToPlot(key: number) {
    const dataId = this.selectedObject.object_id + this.selectedVariable;
    this.$set(this.plotData[key], dataId, {
      data: this.currentData.getColumn(this.selectedVariable),
      index: this.currentData.getColumn("time"),
      units: getVariableUnits(this.selectedVariable),
      name: this.currentName()
    });
  }
  removeFromPlot(key: number, dataId: string) {
    this.$delete(this.plotData[key], dataId);
  }
  createPlot() {
    const index = getIndex();
    this.$set(this.plotData, index, {});
  }
  removePlot(index: number) {
    this.$delete(this.plotData, index);
  }
  filteredObjects(toFilter: Array<Record<string, any>>) {
    // Filter out summary data
    return toFilter.filter(x => {
      return !(
        x.definition.type.includes(" vs ") ||
        x.definition.type.includes("summary")
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
        .filter((y: string) => y != "time" && y != "month");
    } else {
      return [];
    }
  }
  get timezone() {
    return this.job.definition.parameters.time_parameters.timezone;
  }
  currentName() {
    let source = "Uploaded";
    if (this.dataSource == "results") {
      source = "Calculated";
    }
    const dataType = this.selectedObject.definition.type;
    const varName = getVariableDisplayName(this.selectedVariable);
    const units = getVariableUnits(this.selectedVariable);
    return `${source} ${dataType} ${varName} [${units}]`;
  }
  @Watch("selectedObject")
  updateData() {
    this.selectedVariable = "";
    if (this.selectedObject) {
      this.loadingData = true;
      this.loadData().then(data => {
        this.currentData = data;
        this.loadingData = false;
      });
    }
  }
  variableName(varName: string) {
    return getVariableDisplayName(varName);
  }
}
</script>
