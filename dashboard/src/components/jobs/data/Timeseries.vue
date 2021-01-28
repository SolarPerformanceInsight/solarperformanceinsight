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
    // Have to build times manually because calling .toArray() on the time
    // column results in a double length array with alternative 0 values
    // with apache-arrow 3.0.0
    const index = this.tableData.getColumn("time");
    const dateTimes: Array<Date> = [];
    for (let i = 0; i < index.length; i ++) {
      dateTimes.push(new Date(index.get(i)));
    }
    return dateTimes;
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
