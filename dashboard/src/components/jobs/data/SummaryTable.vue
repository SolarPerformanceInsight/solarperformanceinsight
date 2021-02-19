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
import { getVariableUnits } from "@/utils/units";

import { Table } from "apache-arrow";

const headerMap = {
  "actual_energy": "actual vs expected energy",
  "expected_energy": "actual vs expected energy",
  "difference": "actual vs expected energy",
  "ratio": "actual vs expected energy",
  "plane_of_array_insolation": "monthly summary",
  "effective_insolation": "monthly summary",
  "total_energy": "monthly summary",
  "average_daytime_cell_temperature": "monthly summary",
}

@Component
export default class SummaryTable extends Vue {
  @Prop() tableData!: Record<string, Table>;

  get headers() {
    if ("actual vs expected energy" in this.tableData){
      return [
        "month",
        "actual_energy",
        "expected_energy",
        "difference",
        "ratio",
        "plane_of_array_insolation",
        "average_daytime_cell_temperature",
      ];
    } else {
      return [
        "month",
        "total_energy",
        "plane_of_array_insolation",
        "effective_insolation",
        "average_daytime_cell_temperature"
      ];
    }
  }
  displayName(varName: string) {
    const units = getVariableUnits(varName);
    const name = getVariableDisplayName(varName);
    if (units) {
      return `${name} [${units}]`;
    } else {
      return name;
    }
  }
}
</script>
