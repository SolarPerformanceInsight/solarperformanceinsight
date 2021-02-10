<template>
  <div class="summary-table">
    <table
      class="striped-table result-summary"
      :style="`--numCol: ` + headers.length"
    >
      <thead>
        <tr>
          <th v-for="(header, i) of headers" :key="i">
            {{ displayName(header) }}
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
import { getVariableDisplayName } from "@/utils/displayNames";

@Component
export default class SummaryTable extends Vue {
  @Prop() tableData!: any;

  get headers() {
    // maybe determine grouping/leftmost column label dynamically?
    return this.tableData.schema.fields.map((x: any) => x.name);
  }
  displayName(varName: string) {
    return getVariableDisplayName(varName);
  }
}
</script>
