<template>
  <div v-if="tableData" class="summary-table">
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
        <tr v-for="(row, i) of mergedTableData" :key="i">
          <td v-for="(col, j) of headers" :key="j">
            {{ formatValues(col, row[col]) }}
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

/*  Maps variables to the type of result to find the variable in.*/
const headerMap: Record<string, string> = {
  actual_energy: "actual vs expected energy",
  expected_energy: "actual vs expected energy",
  difference: "actual vs expected energy",
  ratio: "actual vs expected energy",
  plane_of_array_insolation: "monthly summary",
  effective_insolation: "monthly summary",
  total_energy: "monthly summary",
  average_daytime_cell_temperature: "monthly summary"
};

// collection of anonymous functions for displaying values
const formatFuncs = {
  actual_energy: (x: number) => x.toFixed(0),
  weather_adjusted_energy: (x: number) => x.toFixed(0),
  expected_energy: (x: number) => x.toFixed(0),
  difference: (x: number) => x.toFixed(0),
  ratio: (x: number) => (x * 100).toFixed(1),
  plane_of_array_insolation: (x: number) => x.toFixed(0),
  effective_insolation: (x: number) => x.toFixed(0),
  total_energy: (x: number) => x.toFixed(0),
  average_daytime_cell_temperature: (x: number) => x.toFixed(0)
};

@Component
export default class SummaryTable extends Vue {
  @Prop() tableData!: Record<string, Table>;

  get headers() {
    if ("actual vs weather adjusted reference" in this.tableData) {
      return [
        "month",
        "actual_energy",
        "weather_adjusted_energy",
        "difference",
        "ratio"
      ];
    } else if ("actual vs expected energy" in this.tableData) {
      return [
        "month",
        "actual_energy",
        "expected_energy",
        "difference",
        "ratio",
        "plane_of_array_insolation",
        "average_daytime_cell_temperature"
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
  get mergedTableData() {
    const data = [];
    const firstKey = Object.keys(this.tableData)[0];
    if (firstKey) {
      data.push(this.tableData[firstKey].getColumn("month"));
      this.headers.forEach((header: string) => {
        if (header == "month") {
          return;
        }
        let dataType = firstKey;

        // Jobs with 'actual vs weather adjusted reference' results do
        // not contain any other monthly summary data to be merged and
        // contain overlapping fields, so just access expected headers
        // directly.
        if (dataType != "actual vs weather adjusted reference") {
          dataType = headerMap[header];
        }
        const dataTable = this.tableData[dataType];
        if (dataTable) {
          data.push(dataTable.getColumn(header));
        }
      });
      return Table.new(...data);
    } else {
      return null;
    }
  }
  formatValues(variable: string, value: string | number) {
    try {
      // @ts-expect-error
      return formatFuncs[variable](value);
    } catch {
      return value;
    }
  }
}
</script>
