<template>
  <div class="custom-plot-definer" v-if="dataObjects && resultObjects">
    Click
    <i>New Plot</i>
    to create a new configurable timeseries plot from the the modeled and
    uploaded data.
    <br />
    <button @click="createPlot">
      New Plot
    </button>
    <div v-for="(pd, id) in plotData" :key="id" class="custom-plot">
      Select a data source and variable and click
      <i>Add to Plot</i>
      to plot the variable below.
      <br />
      <!-- Select whether to choose results or data -->
      <select v-model="dataSources[id]" @change="setDataOption(id)">
        <option value="results">Results</option>
        <option value="upload">Uploaded Data</option>
      </select>
      <!-- Select the data or result to add to the plot -->
      <select v-model="selectedObjects[id]" @change="updateData(id)">
        <option
          v-for="dataOption of dataOptions(id)"
          :value="dataOption"
          :key="dataOption.object_id"
        >
          {{ dataOption.definition.type }}
          {{ dataOption.definition.schema_path }}
        </option>
      </select>
      <!-- Select the variable to add -->
      <select
        v-model="selectedVariables[id]"
        v-if="selectedObjects[id]"
        @change="setUnits(id)"
      >
        <option value="">Select A Variable</option>
        <option
          v-for="variable in variables[id]"
          :key="variable"
          :value="variable"
        >
          {{ variableName(variable) }}
        </option>
      </select>
      <select v-model="units[id]" v-if="convertableVariables[id]">
        <option
          v-for="units of getUnitOptions(selectedVariables[id])"
          :key="units"
          :value="units"
        >
          {{ units }}
        </option>
      </select>
      <button :disabled="!selectedVariables[id]" @click="addToPlot(id)">
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
          <a
            role="button"
            class="warning-text"
            @click="removeFromPlot(id, dataId)"
          >
            (remove)
          </a>
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
import { Component, Vue, Prop } from "vue-property-decorator";
import MultiTimeseriesPlots from "@/components/jobs/data/MultiTimeSeries.vue";

import * as Jobs from "@/api/jobs";
import { Table } from "apache-arrow";
import { getIndex } from "@/utils/fieldIndex";
import { getVariableDisplayName } from "@/utils/displayNames";
import { getVariableUnits } from "@/utils/units";
import { getUnitConverter, getUnitOptions } from "@/utils/unitConversion";

Vue.component("multi-plot", MultiTimeseriesPlots);

@Component
export default class CustomPlots extends Vue {
  @Prop() job!: Record<string, any>;
  @Prop() resultObjects!: Array<Record<string, any>>;

  // Acutal API data objects to handle
  toPlot!: Record<string, any>;

  // component control properties
  dataSources!: Record<number, string>;
  selectedObjects!: Record<number, Record<string, any>>;
  loadedTimeseries!: Record<string, any>;
  loadingData!: boolean;
  variables!: Record<number, Array<string>>;
  selectedVariables!: Record<string, string>;
  units!: Record<number, string>;

  plotData!: Record<number, any>;

  data() {
    return {
      dataSources: {},
      selectedObjects: {},
      selectedVariables: {},
      loadedTimeseries: {},
      loadingData: false,
      variables: {},
      toPlot: {},
      plotData: {},
      units: {}
    };
  }
  addToPlot(key: number) {
    const data_object_id = this.selectedObjects[key].object_id;
    const dataId = data_object_id + this.selectedVariables[key];
    const column = this.loadedTimeseries[data_object_id].getColumn(
      this.selectedVariables[key]
    );
    let columnData: Array<any>;
    const firstValue = column.get(0);
    // get a converter function if necessary
    const converter = getUnitConverter(
      getVariableUnits(this.selectedVariables[key]),
      this.units[key]
    );
    if (firstValue && firstValue.length && firstValue.length > 1) {
      // Handles values like int64 which are encoded as length 2 int32 array
      columnData = [];
      for (let i = 0; i < column.length; i++) {
        if (converter) {
          columnData.push(converter(parseFloat(column.get(i))));
        } else {
          columnData.push(parseFloat(column.get(i)));
        }
      }
    } else {
      columnData = column.toArray();
      if (converter) {
        columnData = columnData.map(converter);
      }
    }
    this.$set(this.plotData[key], dataId, {
      data: columnData,
      index: this.loadedTimeseries[data_object_id].getColumn("time"),
      units: this.units[key],
      name: this.currentName(key)
    });
  }
  removeFromPlot(key: number, dataId: string) {
    this.$delete(this.plotData[key], dataId);
  }
  createPlot() {
    const index = getIndex();
    this.dataSources[index] = "results";
    this.$set(this.selectedVariables, index, "");
    this.setDataOption(index);
    this.$set(this.plotData, index, {});
  }
  removePlot(index: number) {
    this.$delete(this.plotData, index);
  }
  filteredObjects(toFilter: Array<Record<string, any>>) {
    // Filter out summary data
    return toFilter.filter(x => {
      const dataType = x.definition.type;
      return !(
        dataType.includes(" vs ") ||
        dataType.includes("summary") ||
        dataType.includes("flag")
      );
    });
  }
  get dataObjects() {
    return this.job.data_objects;
  }
  dataOptions(key: number) {
    if (this.dataSources[key] == "results") {
      return this.filteredObjects(this.resultObjects);
    } else {
      return this.filteredObjects(this.dataObjects);
    }
  }
  async loadData(key: number) {
    let fetchFunc = Jobs.getData;

    if (this.dataSources[key] == "results") {
      fetchFunc = Jobs.getSingleResult;
    }
    const token = await this.$auth.getTokenSilently();
    const object_id = this.selectedObjects[key].object_id;

    const response = await fetchFunc(
      token,
      this.job.object_id,
      object_id
    ).then(payload => payload.arrayBuffer());

    return Table.from([new Uint8Array(response)]);
  }
  setVariables(key: number) {
    const object_id = this.selectedObjects[key].object_id;
    let data = [];
    if (this.loadedTimeseries[object_id]) {
      data = this.loadedTimeseries[object_id].schema.fields
        .map((x: any) => x.name)
        .filter((y: string) => y != "time" && y != "month");
    }
    this.$set(this.variables, key, data);
  }
  get timezone() {
    return this.job.definition.parameters.time_parameters.timezone;
  }

  get convertableVariables() {
    const convertable: Array<string> = [];
    for (const index in this.selectedVariables) {
      const variable = this.selectedVariables[index];
      // @ts-expect-error
      convertable[index] = ["W", "Wh", "W/m^2"].includes(
        getVariableUnits(variable)
      );
    }
    return convertable;
  }

  currentName(key: number) {
    let source = "Uploaded";
    if (this.dataSources[key] == "results") {
      source = "Calculated";
    }
    const dataType = this.selectedObjects[key].definition.type;
    const varName = getVariableDisplayName(this.selectedVariables[key]);
    const units = this.units[key];
    return `${source} ${dataType} ${varName} [${units}]`;
  }
  updateData(key: number) {
    this.$set(this.selectedVariables, key, "");
    if (this.selectedObjects[key]) {
      const object_id = this.selectedObjects[key].object_id;
      if (!(object_id in this.loadedTimeseries)) {
        this.loadingData = true;
        this.loadData(key).then(data => {
          this.loadedTimeseries[object_id] = data;
          this.setVariables(key);
          this.selectedVariables[key] = "";
          this.loadingData = false;
        });
      } else {
        this.setVariables(key);
        this.selectedVariables[key] = "";
      }
    }
  }
  variableName(varName: string) {
    return getVariableDisplayName(varName);
  }
  setDataOption(key: number) {
    this.selectedObjects[key] = this.dataOptions(key)[0];
    this.updateData(key);
  }
  setUnits(key: number) {
    const variable = this.selectedVariables[key];
    console.log("VARIABLE: '", variable, "'");
    if (variable && variable != "") {
      this.units[key] = getVariableUnits(variable);
    }
  }
  getUnitOptions(variable: string) {
    return getUnitOptions(variable);
  }
}
</script>
<style>
.custom-plot {
  box-shadow: 1px 1px 6px #555;
  margin: 0.5em 0;
  padding: 1em;
}
</style>
