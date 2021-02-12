84;0;0c
<template>
  <div class="timeseries-plot">
    <slot></slot>
    Download:
    <button @click="downloadData('text/csv')">CSV</button>
    <button @click="downloadData('application/vnd.apache.arrow.file')">
      Apache Arrow
    </button>
    <br />
    <div :id="id"></div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { Table } from "apache-arrow";
import Plotly from "plotly.js-basic-dist";
import adjustPlotTime from "@/utils/adjustPlotTimes";
import { getVariableDisplayName } from "@/utils/displayNames";

@Component
export default class TimeseriesPlot extends Vue {
  @Prop() timeseriesData!: Array<Record<string, any>>;
  @Prop() tz!: string;
  config = { responsive: true };

  // should update to be unique if we want multiple plots on a page
  id = "thePlot";

  convertIndex(index: any) {
    const dateTimes: Array<Date> = [];
    for (let i = 0; i < index.length; i++) {
      dateTimes.push(adjustPlotTime(index.get(i), this.tz));
    }
    return dateTimes;
  }
  get plotData(): Partial<Plotly.PlotData>[] {
    return this.timeseriesData.map((data: Record<string, any>) => {
      return {
        x: this.convertIndex(data.index),
        y: data.data.toArray(),
        name: data.name,
        type: "scatter"
      }
    });
  }
  displayName(varName: string) {
    return getVariableDisplayName(varName);
  }
  get plotTitle() {
    return `lots o THINGS`;
  }
  get layout() {
    return {
      title: this.plotTitle,
      xaxis: {
        title: `Time (${this.tz})`
      },
      yaxis: {
        title: "Datetime"
      }
    };
  }
  async mounted() {
    await Plotly.react(this.id, this.plotData, this.layout, this.config);
  }
  downloadData(contentType: string) {
    this.$emit("download-timeseries", contentType);
  }
}
</script>
