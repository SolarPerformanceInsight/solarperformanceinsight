<template>
  <div class="timeseries-plot">
    <button @click="removePlot">Delete Plot</button>
    <slot></slot>
    <button @click="downloadData">Download CSV</button>
    <button @click="editTitle = true">Edit plot title</button>
    <div v-if="editTitle">
      <label for="plot-title">New Plot Title:&nbsp;</label>
      <input v-model="title" />
      <button
        @click="
          editTitle = false;
          redraw();
        "
      >
        Update Title
      </button>
    </div>
    <br />
    <div :id="plotDivId" class="timeseries-plot-wrapper"></div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";

import Plotly from "plotly.js-basic-dist";
import adjustPlotTime from "@/utils/adjustPlotTimes";
import papa from "papaparse";
import { getVariableDisplayName } from "@/utils/displayNames";
import downloadFile from "@/utils/downloadFile";

@Component
export default class TimeseriesPlot extends Vue {
  @Prop() timeseriesData!: Record<string, any>;
  @Prop() index!: number;
  @Prop() tz!: string;
  config = { responsive: true };
  subplots!: Array<string>;
  editTitle!: boolean;
  title!: string;

  data() {
    return {
      subplots: [],
      editTitle: false,
      title: ""
    };
  }
  convertIndex(index: any) {
    const dateTimes: Array<Date> = [];
    for (let i = 0; i < index.length; i++) {
      dateTimes.push(adjustPlotTime(index.get(i), this.tz));
    }
    return dateTimes;
  }
  get plotData(): any {
    //Array<Partial<Plotly.PlotData>[]> {
    const allData = Object.values(this.timeseriesData).map(
      (data: Record<string, any>) => {
        return {
          x: this.convertIndex(data.index),
          y: data.data.toArray(),
          name: data.name,
          type: "scatter",
          showlegend: true
        };
      }
    );
    this.subplots = [];
    const dataTypes = new Set(allData.map(x => typeof x.y[0]));
    const subplotData: Array<Array<Partial<Plotly.PlotData>>> = [];
    dataTypes.forEach((dataType, i) => {
      const filteredData = allData.filter(data => typeof data.y[0] == dataType);
      // @ts-expect-error
      filteredData.forEach(data => (data.yaxis = `y${i}`));
      //@ts-expect-error
      subplotData.push(filteredData);
    });
    // return subplotData;
    return allData;
  }
  displayName(varName: string) {
    return getVariableDisplayName(varName);
  }
  get plotTitle() {
    return this.title ? this.title : `Custom Plot ${this.index}`;
  }
  get layout() {
    return {
      title: this.plotTitle,
      grid: {
        rows: this.plotData.length
      },
      xaxis: {
        title: `Time (${this.tz})`
      },
      yaxis: {
        title: "Value"
      }
    };
  }
  get plotDivId() {
    return `timeseries-plot-${this.index}`;
  }
  async mounted() {
    await Plotly.react(this.plotDivId, this.plotData, this.layout, this.config);
  }
  downloadData() {
    // TODO: handle index issues?
    const csvData = this.plotData[0].x.map((time: string, i: number) => {
      const data = this.plotData.reduce(
        (current: Record<string, any>, traceData: Record<string, any>) => {
          current[traceData.name] = traceData.y[i];
          return current;
        },
        {}
      );
      return {
        time: time,
        ...data
      };
    });

    const downloadData = papa.unparse(
      { fields: Object.keys(csvData[0]), data: csvData },
      { header: true }
    );
    const csv = new Blob([downloadData], { type: "text/csv" });
    downloadFile(`${this.plotTitle}.csv`, csv);
  }
  removePlot() {
    this.$emit("remove-plot", this.index);
  }
  @Watch("timeseriesData", { deep: true })
  redraw() {
    console.log("redrawing");
    Plotly.react(this.plotDivId, this.plotData, this.layout, this.config);
  }
}
</script>
<style scoped>
.timeseries-plot-wrapper {
  min-height: 450px;
}
</style>
