<template>
  <div class="summary-table">
    <table class="result-summary" :style="`--numCol: ` + headers.length">
      <thead>
        <tr>
          <th v-for="(header, i) of headers" :key="i">
            {{ header }}
          </th>
        <tr/>
      </thead>
      <tbody>
        <tr v-for="(row, i) of rows" :key="i" >
          <td v-for="(val, j) of row" :key="j">
            {{ val }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component export default class SummaryTable extends Vue {
  @Prop() data!: any;

  get headers() {
    // maybe determine grouping/leftmost column label dynamically?
    return ["month", "AC Energy", "Global Plane of Array Irradiance", "Effective Irradiance", "Cell Temperature"];
  }
  get rows() {
    return [
      ["January", 99.87, 400, 359, 25],
      ["February", 99.87, 400, 359, 25],
      ["March", 99.87, 400, 359, 25],
      ["April", 99.87, 400, 359, 25],
      ["May", 99.87, 400, 359, 25],
      ["June", 99.87, 400, 359, 25],
      ["July", 99.87, 400, 359, 25],
      ["August", 99.87, 400, 359, 25],
      ["September", 99.87, 400, 359, 25],
      ["October", 99.87, 400, 359, 25],
      ["November", 99.87, 400, 359, 25],
      ["December", 99.87, 400, 359, 25],
    ];
  }
}
</script>
<style scoped="true">
table {
  display: grid;
  border-collapse: collapse;
  grid-template-columns: repeat(var(--numCol), auto);
}
table th {
  padding: .5em;
  text-align: left;
}
thead,
tbody,
tr {
  display: contents;
}
td {
  padding: .5em;
}
tr:nth-child(even) td{
  background-color: #eee;
}
</style>
