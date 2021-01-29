<template>
  <div class="timeseries-plot">
    Download:
    <button @click="downloadData('text/csv')">CSV</button>
    <button @click="downloadData('application/vnd.apache.arrow.file')">
      Apache Arrow
    </button>
    <br />
    Variable:
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
import Plotly from "plotly.js-basic-dist";

@Component
export default class TimeseriesPlot extends Vue {
  @Prop() timeseriesData!: Table;
  @Prop() title!: string;
  config = { responsive: true };
  column!: string;

  // should update to be unique if we want multiple plots on a page
  id = "thePlot";

  data() {
    return {
      column: ""
    };
  }
  get yData() {
    return this.timeseriesData.getColumn(this.column).toArray();
  }
  get xData() {
    // Have to build times manually because calling .toArray() on the time
    // column results in a double length array with alternative 0 values
    // with apache-arrow 3.0.0
    const index = this.timeseriesData.getColumn("time");
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
    return this.timeseriesData.schema.fields
      .map(x => x.name)
      .filter(x => x !== "time");
  }
  get plotTitle() {
    return `${this.title} ${this.column}`;
  }
  get layout() {
    return {
      title: this.plotTitle,
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
    await Plotly.react(this.id, this.plotData, this.layout, this.config);
  }
  @Watch("column")
  redraw() {
    Plotly.react(this.id, this.plotData, this.layout, this.config);
  }
  @Watch("timeseriesData")
  changeData() {
    this.column = this.availableFields[0];
  }
  downloadData(contentType: string) {
    this.$emit("download-timeseries", contentType);
  }
}
</script>
