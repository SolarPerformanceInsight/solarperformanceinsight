<template>
  <div class="timeseries-plot">
    <p>I will be a plot</p>
    {{ tableData }}
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component
export default class TimeseriesPlot extends Vue {
  // Add apache modulea and load the table
  @Prop() tableData!: any;
}
</script>
