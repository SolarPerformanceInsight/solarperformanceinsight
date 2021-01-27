<template>
  <div class="timeseries-plot">
    <p>I will be a plot</p>
    <div :id="id"></div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { Table } from "apache-arrow";
import Plotly from "plotly.js";

import { getIndex } from "@/utils/fieldIndex";

@Component
export default class TimeseriesPlot extends Vue {
  // Add apache modulea and load the table
  @Prop() tableData!: Table;
  // Expected to tell us how to find data
  @Prop() dataType!: string;
  layout!: Record<string, any>;
  id = "thePlot";

  data() {
    return {
      layout: { // TODO: make this computed
        xaxis: {
          title: "Time",
        },
        yaxis: {
          title: "The Measurement"
        }
      }
    }
  }
  get yData() {return this.tableData.getColumn("ghi").toArray();}
  get xData() {
    return this.tableData.getColumn("time").toArray().map(
      (x: number) => {
        return new Date(x * 1000);
      }
    );
  }
  get plotData(): Partial<Plotly.PlotData>[] {
    return [{
      x: this.xData,
      y: this.yData,
      type: "scatter"
    }];
  }
  async mounted() {
    const plot =  await Plotly.react(
      this.id,
      this.plotData,
      this.layout
    );
  }
}
</script>
