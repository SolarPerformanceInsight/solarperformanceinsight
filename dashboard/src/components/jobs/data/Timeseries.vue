<template>
  <div class="timeseries-plot">
    Plot:
    <select v-model="column">
      <option v-for="(field, i) in availableFields" :key="i">
        {{ field }}
      </option>
    </select>
    <div :id="id"></div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { Table } from "apache-arrow";
import Plotly from "plotly.js";

@Component
export default class TimeseriesPlot extends Vue {
  // Add apache modulea and load the table
  @Prop() tableData!: Table;
  // Expected to tell us how to find data
  @Prop() dataType!: string;
  column!: string;

  id = "thePlot";

  data() {
    return {
      column: ""
    };
  }
  get yData() {
    return this.tableData.getColumn(this.column).toArray();
  }
  get xData() {
    // Have to build times manually because calling .toArray() on the time
    // column results in a double length array with alternative 0 values
    // with apache-arrow 3.0.0
    const index = this.tableData.getColumn("time");
    const dateTimes: Array<Date> = [];
    for (let i = 0; i < index.length; i++) {
      dateTimes.push(new Date(index.get(i)));
    }
    return dateTimes;
  }
  get plotData(): Partial<Plotly.PlotData>[] {
    return [
      {
        x: this.xData,
        y: this.yData,
        type: "scatter"
      }
    ];
  }
  get availableFields() {
    return this.tableData.schema.fields
      .map(x => x.name)
      .filter(x => x !== "time");
  }
  get layout() {
    return {
      xaxis: {
        title: "Time"
      },
      yaxis: {
        title: this.column
      }
    };
  }
  async mounted() {
    this.column = this.availableFields[0];
    await Plotly.react(this.id, this.plotData, this.layout);
  }
  @Watch("column")
  redraw() {
    Plotly.react(this.id, this.plotData, this.layout);
  }
}
</script>
