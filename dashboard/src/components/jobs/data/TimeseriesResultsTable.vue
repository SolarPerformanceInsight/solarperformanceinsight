<template>
  <div class="summary-table">
    <table
      class="striped-table result-summary"
      style="--numCol: 5"
    >
      <thead>
        <tr>
          <th>
            Result or Uploaded
          </th>
          <th>
            System Component
          </th>
          <th>
            Data Type
          </th>
          <th>
            Available Variables
          </th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i ) of tableData" :key="i">
          <td>
            {{ row.source }}
          </td>
          <td>
            {{ row.path }}
          </td>
          <td>
            {{ row.type }}
          </td>
          <td>
            <span v-for="(v, j) of row.variables" :key="j">
            {{ v }}<br/>
            </span>
          </td>
          <td>
            <span v-if="row.present">
            <button>Download CSV</button>
            <button>Download Arrow</button>
            </span>
            <span v-else>
               Not Uploaded
            </span>
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

@Component
export default class TimeseriesTable extends Vue {
  @Prop() system!: any;
  @Prop() dataObjects!: any;
  @Prop() resultObjects!: any;

  get tableData() {
    const allData = [];
    if (this.dataObjects) {
      for (const dataObject of this.dataObjects) {
        allData.push({
          source: "Uploaded",
          path: dataObject.definition.schema_path,
          type: dataObject.definition.type,
          variables: dataObject.definition.data_columns.map(this.displayName),
          present: dataObject.definition.present
        });
      }
    }
    if (this.resultObjects) {
      for (const resultObject of this.resultObjects) {
        allData.push({
          source: "Results",
          path: resultObject.definition.schema_path,
          type: resultObject.definition.type,
          variables: ["some", "variables!"],
          present: false
        });
      }
    }
    return allData;
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
