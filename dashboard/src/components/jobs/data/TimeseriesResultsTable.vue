<template>
  <div class="summary-table">
    <table class="striped-table result-summary" style="--numCol: 5">
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
        <tr v-for="(row, i) of tableData" :key="i">
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
            <ul class="pl-0">
              <li v-for="(v, j) of row.variables" :key="j">
                {{ v }}
              </li>
            </ul>
          </td>
          <td>
            <span v-if="row.present">
              <button
                @click="downloadData('text/csv', row.source, row.metadata)"
              >
                Download CSV
              </button>
              <button
                @click="
                  downloadData(
                    'application/vnd.apache.arrow.file',
                    row.source,
                    row.metadata
                  )
                "
              >
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

import * as Jobs from "@/api/jobs";
import downloadFile from "@/utils/downloadFile";
import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";

// Maps types of results to their available variables
const resultVariables: Record<string, Array<string>> = {
  "performance data": ["performance"],
  "weather data": ["effective_irradiance", "poa_global", "cell_temperature"],
  "monthly summary": [
    "total_energy",
    "plane_of_array_insolation",
    "effective_insolation",
    "average_daytime_cell_temperature"
  ],
  "actual vs modeled energy": [
    "actual_energy",
    "modeled_energy",
    "difference",
    "ratio"
  ],
  "weather adjusted performance": ["performance"],
  "actual vs weather adjusted reference": [
    "actual_energy",
    "weather_adjusted_energy",
    "difference",
    "ratio"
  ],
  "daytime flag": ["daytime_flag"]
};

@Component
export default class TimeseriesTable extends Vue {
  @Prop() job!: any;
  @Prop() dataObjects!: any;
  @Prop() resultObjects!: any;
  showUploads!: boolean;

  data() {
    return {
      showUploads: false
    };
  }

  get tableData() {
    const allData = [];

    if (this.resultObjects) {
      for (const resultObject of this.resultObjects) {
        const resultType = resultObject.definition.type;
        if (resultType == "error message") {
          continue;
        }
        const path = resultObject.definition.schema_path;
        const systemComponent = indexSystemFromSchemaPath(
          this.job.definition.system_definition,
          path
        );
        const componentName = `${systemComponent.name} (${path})`;
        try {
          allData.push({
            source: "Results",
            metadata: resultObject,
            path: componentName,
            type: resultType,
            variables: resultVariables[resultType].map(this.displayName),
            present: true
          });
        } catch {
          console.log("Result failure: ", JSON.stringify(resultType));
        }
      }
    }
    if (this.dataObjects) {
      for (const dataObject of this.dataObjects) {
        const path = dataObject.definition.schema_path;
        const systemComponent = indexSystemFromSchemaPath(
          this.job.definition.system_definition,
          path
        );
        const componentName = `${systemComponent.name} (${path})`;
        try {
          allData.push({
            source: "Uploaded",
            metadata: dataObject,
            path: componentName,
            type: dataObject.definition.type,
            variables: dataObject.definition.data_columns.map(this.displayName),
            present: dataObject.definition.present
          });
        } catch {
          console.log("DO failure: ", JSON.stringify(dataObject));
        }
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

  async downloadData(
    contentType: string,
    source: string,
    metadata: Record<string, any>
  ) {
    let fetchFunc = Jobs.getData;
    if (source == "Results") {
      fetchFunc = Jobs.getSingleResult;
    }
    const token = await this.$auth.getTokenSilently();
    const object_id = metadata.object_id;

    const fileContents = await fetchFunc(
      token,
      this.job.object_id,
      object_id,
      contentType
    ).then(response => response.blob());
    const systemComponent = indexSystemFromSchemaPath(
      this.job.definition.system_definition,
      metadata.definition.schema_path
    );
    const componentName = systemComponent.name.replace(/\s/g, "_");
    let ext = "arrow";
    if (contentType.includes("csv")) {
      ext = "csv";
    }
    const dataSource = source.toLowerCase();
    const dataType = metadata.definition.type.replace(/\s/g, "_");
    const filename = `${componentName}_${dataType}_${dataSource}.${ext}`;
    downloadFile(filename, fileContents);
  }
}
</script>
<style scoped="true">
ul {
  padding-left: 1em;
}
</style>
