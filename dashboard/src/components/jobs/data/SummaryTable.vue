<template>
  <div class="summary-table">
    <table class="result-summary" :style="`--numCol: ` + headers.length">
      <thead>
        <tr>
          <th v-for="(header, i) of headers" :key="i">
            {{ header }}
          </th>
        </tr>

        <tr />
      </thead>
      <tbody>
        <tr v-for="(row, i) of tableData" :key="i">
          <td v-for="(col, j) of headers" :key="j">
            {{ row[col] }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component
export default class SummaryTable extends Vue {
  @Prop() tableData!: any;

  get headers() {
    // maybe determine grouping/leftmost column label dynamically?
    return this.tableData.schema.fields.map((x: any) => x.name);
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
  padding: 0.5em;
  text-align: left;
}
thead,
tbody,
tr {
  display: contents;
}
td {
  padding: 0.5em;
}
tr:nth-child(even) td {
  background-color: #eee;
}
</style>
