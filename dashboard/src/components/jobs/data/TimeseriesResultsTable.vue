<template>
  <div class="summary-table">
    <table
      class="striped-table result-summary"
      style="--numCol: 5"
    >
      <thead>
        <tr>
          <th>
            Data Source
          </th>
          <th>
            System Component
          </th>
          <th>
            Data Type
          </th>
          <th>
            Variables
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
            <button @click="downloadData('text/csv', row.source, row.metadata)">Download CSV</button>
            <button @click="downloadData('application/vnd.apache.arrow.file', row.source, row.metadata)">
              Download Arrow
            </button>
            </span>
            <span class="warning-text" v-else>
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
          metadata: dataObject,
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
          metadata: resultObject.object_id,
          path: resultObject.definition.schema_path,
          type: resultObject.definition.type,
          variables: ["some", "variables!"],
          present: true
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

  downloadData(contentType: string, source: string, object_id: string) {
    this.emit("download-data", {
      contentType,
      source,
      object_id
    });
  }
}
</script>
