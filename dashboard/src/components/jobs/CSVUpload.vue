<!--
Component that handles upload and extracting of headers for a single file.
Takes the following props that can be extracted from job metadata.
  - temperature_type: string - the source of module temperature. One of:
    - "module": requires that "module_temperature" be provided in the file.
    - "cell": requires that "cell_temperature" be provided in the file.
    - "air": requires that "temp_air" and "wind_speed" be provided".
  - granularity: string: What part of the spec the weather data is
    associated with. One of:
    - "system": System wide data in the file.
    - "inverter": Data for each inverter in the file.
    - "array": Data for each array in the file.
  - system: System: The system to map data onto.
  - data_objects: array - Array of data objects created by the api.
-->
<template>
  <div class="csv-upload">
    <slot>Upload your weather data</slot>
    <br />
    <label>
      CSV headers are on line:
      <input
        id="header-line"
        type="number"
        step="1"
        min="0"
        @change="enforceDataStartOrder"
        v-model.number="headerLine"
      />
    </label>
    <help
      helpText="The line number where headers are found in your CSV. For files without headers, set this value to 0."
    />
    <br />
    <label for="data-start-line">Data begins on line:</label>
    <input
      id="data-start-line"
      type="number"
      step="1"
      :min="headerLine + 1"
      @change="adjustHeaderDataLine"
      v-model.number="dataStartLine"
    />
    <br />
    <label for="csv-upload" class="mt-1">
      Select a file with {{ dataType }} containing:
    </label>
    <ul>
      <li>{{ timeParameterSummary }}</li>
      <li>One {{ indexField }} field.</li>
      <li>
        The following variables for
        <template v-if="granularity == 'system'">the</template>
        <template v-else>each</template>
        {{ granularity }}:
        <ul>
          <li v-for="req of requiredFieldSummary" :key="req">{{ req }}</li>
        </ul>
      </li>
    </ul>
    <input
      id="csv-upload"
      type="file"
      accept="text/csv"
      @change="processFile"
    />
    <template v-if="processingFile">
      <div class="file-processing-container">
        <div class="loading">
          Processing File
          <span class="loading-container"></span>
        </div>
      </div>
    </template>
    <template v-if="parsingErrors">
      <div class="mt-1 warning">
        Errors encountered processing your csv.
        <ul>
          <li v-for="(error, i) of parsingErrors" :key="i">
            <b>{{ error.type }}</b>
            : {{ error.message }}
          </li>
        </ul>
      </div>
    </template>
    <transition name="fade">
      <div v-if="promptForMapping">
        <csv-preview
          :headers="headers"
          :csvData="csvPreview"
          :mapping="headerMapping"
          :currentlySelected="currentSelection"
        />
      </div>
    </transition>
    <transition name="fade">
      <div v-if="promptForMapping && !processingFile">
        <csv-mapper
          @new-mapping="processMapping"
          :indexField="indexField"
          :system="system"
          :granularity="granularity"
          :data_objects="data_objects"
          :headers="headers"
          :required="required"
        >
          <p>
            Select which columns in your file contain data for the required
            variables. Data can be uploaded using the button below once the
            required variables are mapped to columns for
            {{
              granularity == "system" ? "the system" : `each ${granularity}`
            }}.
          </p>
        </csv-mapper>
        <button :disabled="!mappingComplete" @click="uploadData">
          Upload Data
        </button>
        <span v-if="!mappingComplete">
          All required fields must be mapped before upload
        </span>
        <div v-if="uploadingData" class="upload-progress">
          <b>Upload Progress</b>
          <ul class="upload-statuses">
            <li v-for="(o, i) in uploadStatuses" :key="i">
              {{ o.component.name }}:
              <span v-if="o.status == 'uploading'">
                uploading
                <span class="loading-container"></span>
              </span>
              <span v-else-if="['waiting', 'done'].includes(o.status)">
                <b>{{ o.status }}</b>
              </span>
              <span v-else class="warning-text">{{ o.status }}</span>
            </li>
          </ul>
        </div>
      </div>
    </transition>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { System } from "@/types/System";

import parseCSV from "@/utils/parseCSV";
import { mapToCSV, Mapping, CSVHeader } from "@/utils/mapToCSV";
import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";
import { getVariableDisplayName } from "@/utils/displayNames";

import { addData } from "@/api/jobs";

import CSVPreview from "@/components/jobs/data/CSVPreview.vue";

Vue.component("csv-preview", CSVPreview);

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

@Component
export default class CSVUpload extends Vue {
  @Prop() job!: Record<string, any>;
  @Prop() system!: System;
  @Prop() temperature_type!: string;
  @Prop() data_objects!: Array<Record<string, any>>;
  mapping!: Record<string, Record<string, Mapping>>;
  promptForMapping!: boolean;
  headers!: Array<CSVHeader>;
  csv!: string;
  csvData!: Array<Record<string, Array<string | number>>>;
  required!: Array<string>;
  mappingComplete!: boolean;

  processingFile!: boolean;
  parsingErrors!: Record<string, any> | null;
  headerLine!: number;
  dataStartLine!: number;

  uploadingData!: boolean;
  uploadStatuses!: Record<string, any>;

  // passed to preview to highlight columns
  currentSelection!: string | null;

  data() {
    return {
      mapping: {},
      processingFile: false,
      parsingErrors: null,
      promptForMapping: false,
      headers: [],
      required: this.getRequired(),
      mappingComplete: false,
      csv: "",
      csvData: [{}],
      uploadingData: false,
      uploadStatuses: {},
      headerLine: 1,
      dataStartLine: 2,
      currentSelection: null
    };
  }
  get jobId() {
    return this.job.object_id;
  }
  get dataType() {
    return this.data_objects[0].definition.type;
  }
  get totalMappings() {
    const nonIndexRequired = this.required.filter(x => x != this.indexField);
    return 1 + nonIndexRequired.length * this.data_objects.length;
  }
  get csvPreview() {
    return this.csvData.slice(0, 5);
  }
  get headerMapping() {
    // Special mapping of headers to expected variables for the csv preview
    const newMap: Record<string, any> = {};

    // Invert mappings so they are accessible by header
    for (const loc in this.mapping) {
      const mapping = this.mapping[loc];
      for (const variable in mapping) {
        let header: string | number;
        if (mapping[variable].csv_header) {
          if (
            mapping[variable].csv_header.header == "" ||
            mapping[variable].csv_header.header
          ) {
            // @ts-expect-error
            header = mapping[variable].csv_header.header;
          } else {
            header = mapping[variable].csv_header.header_index;
            //header = `Column ${header_index}`;
          }
          if (variable == this.indexField && newMap[this.indexField]) {
            continue;
          }
          newMap[header] = variable;
        }
      }
    }
    return newMap;
  }
  get indexField() {
    // Return the name of the expected time/index column.
    if (this.required.includes("time")) {
      return "time";
    } else {
      return "month";
    }
  }
  get timeParameterSummary() {
    if (this.dataType.includes("monthly")) {
      return "Data for each month of the year.";
    }
    const timeParameters = this.job.definition.parameters.time_parameters;
    const start = timeParameters.start;
    const end = timeParameters.end;
    const step = timeParameters.step / 60;
    return `Data from ${start} to ${end} with ${step} minutes between data points.`;
  }
  get requiredFieldSummary() {
    const nonIndexRequired = this.required.filter(x => x != this.indexField);
    const displayNames = nonIndexRequired.map(x => getVariableDisplayName(x));
    return displayNames;
  }
  removeMetadata(csv: string) {
    // Determine the characters used for line separation
    const lineSep = csv.indexOf("\r") >= 0 ? "\r\n" : "\n";

    // parse out header
    let linesRead = 0;
    let headerString = "";

    // Read in a line as the header until we reach the header line defined
    // by the user.
    for (linesRead; linesRead < this.headerLine; linesRead++) {
      headerString = csv.substring(0, csv.indexOf(lineSep));
      csv = csv.substring(csv.indexOf(lineSep) + lineSep.length);
    }

    // skip lines until we reach the start of data in the csv
    for (linesRead; linesRead < this.dataStartLine - 1; linesRead++) {
      csv = csv.substring(csv.indexOf(lineSep) + lineSep.length);
    }
    if (headerString.length > 0) {
      csv = headerString + lineSep + csv;
    }
    return csv;
  }
  storeCSV(csv: string | null) {
    this.promptForMapping = false;
    this.csvData = [{}];
    this.mapping = {};
    if (csv) {
      this.csv = csv;
    } else {
      csv = this.csv;
    }
    this.parsingErrors = null;
    // Parse the csv into an object mapping csv-headers to arrays of column
    // data.
    csv = this.removeMetadata(csv);
    const parsingResult = parseCSV(csv.trim(), this.headerLine != 0);
    if (parsingResult.errors.length > 0) {
      const errors: Record<string, any> = {};
      parsingResult.errors.forEach((error, index) => {
        let message = error.message;
        if ("row" in error) {
          message += ` (row: ${error.row})`;
        }
        errors[index] = {
          type: error.type,
          message: message
        };
      });
      this.parsingErrors = errors;
    } else {
      let headers: Array<CSVHeader> = [];
      if (this.headerLine == 0) {
        // @ts-expect-error
        headers = parsingResult.data[0].map((x: string, i: number) => {
          return {
            header_index: i
          };
        });
      } else {
        const csvHeaders = parsingResult.meta.fields;
        if (csvHeaders !== undefined) {
          let duplicates = csvHeaders.filter(
            (header: string, index: number) => {
              return csvHeaders.indexOf(header) != index;
            }
          );
          duplicates = Array.from(new Set(duplicates));
          if (duplicates.length > 0) {
            this.parsingErrors = {
              0: {
                type: "Duplicate CSV Header",
                message: `Cannot parse CSV with duplicate headers. Found duplicates: "${duplicates.join(
                  '","'
                )}".`
              }
            };
          } else {
            headers = csvHeaders.map((header: string, i: number) => {
              return {
                header: header,
                header_index: i
              };
            });
          }
        }
      }
      if (
        !this.parsingErrors &&
        headers &&
        headers.length < this.totalMappings
      ) {
        // Handle case where CSV is parsable but does not contain enough data
        this.parsingErrors = {
          0: {
            type: "Too Few Columns",
            message: `You do not have enough data in this file. The file contains
${headers ? headers.length : 0} columns and ${
              this.totalMappings
            } columns are expected (one
${this.indexField} column, and ${this.required
              .filter(x => x != this.indexField)
              .join(", ")} for
${this.granularity == "system" ? "the" : "each"} ${this.granularity}).`
          }
        };
        this.csvData = [{}];
      }
      if (this.parsingErrors == null) {
        this.csvData = parsingResult.data;
        this.headers = headers ? headers : [];
        this.promptForMapping = true;
      }
    }
    this.processingFile = false;
  }
  processMapping(mapObject: {
    mapping: Record<string, Record<string, string>>;
    complete: boolean;
  }) {
    // Handle a new mapping from the CSVMapper component
    for (const loc in mapObject.mapping) {
      this.$set(this.mapping, loc, mapObject.mapping[loc]);
    }
    this.mappingComplete = mapObject.complete;
  }
  processFile(e: HTMLInputEvent) {
    // Handle a CSV upload, hand of parsing to storeCSV
    if (e.target.files !== null) {
      this.processingFile = true;
      const file = e.target.files[0];
      const reader = new FileReader();
      // @ts-expect-error
      reader.onload = f => this.storeCSV(f.target.result);
      reader.readAsText(file);
    }
  }
  async uploadData() {
    // initialize variables for displaying upload progress to the user
    for (const dataObject of this.data_objects) {
      const initialStatus = {
        status: "waiting",
        errors: null,
        component: indexSystemFromSchemaPath(
          this.system,
          dataObject.definition.schema_path
        )
      };
      // Use set so updloadStatuses is reactive
      this.$set(this.uploadStatuses, dataObject.object_id, initialStatus);
    }

    this.uploadingData = true;
    // function to call when all mapping has been completed. Should complete
    // the mapping process and post to the API
    let success = true;
    for (const dataObject of this.data_objects) {
      // TODO: handle this on a single loc basis instead of looping all at once
      this.uploadStatuses[dataObject.object_id].status = "uploading";
      const loc = dataObject.definition.schema_path;
      const mapping = this.mapping[loc];
      const csv = mapToCSV(this.csvData, mapping);
      const token = await this.$auth.getTokenSilently();
      const response = await addData(
        token,
        this.jobId,
        dataObject.object_id,
        csv
      );
      if (!response.ok) {
        success = false;
        const details = await response.json();
        this.uploadStatuses[dataObject.object_id].status = details.detail;
      } else {
        this.uploadStatuses[dataObject.object_id].status = "done";
      }
    }
    if (success) {
      this.$emit("data-uploaded");
    }
  }
  getRequired() {
    // May need to be updated if required fields are ever different for weather
    // data objects
    return this.data_objects[0].definition.data_columns;
  }
  enforceDataStartOrder() {
    if (this.headerLine >= this.dataStartLine) {
      this.dataStartLine = this.headerLine + 1;
    }
    this.adjustHeaderDataLine();
  }
  updateSelected(selected: string | null) {
    this.currentSelection = selected;
  }
  adjustHeaderDataLine() {
    if (this.promptForMapping) {
      this.processingFile = true;
      this.promptForMapping = false;
      this.storeCSV(null);
    }
  }
  get granularity() {
    if (this.dataType.includes("monthly")) {
      return "system";
    } else {
      let source: any;
      if (
        this.dataType.includes("original") ||
        this.dataType.includes("predicted")
      ) {
        if ("predicted_data_parameters" in this.job.definition.parameters) {
          source = this.job.definition.parameters.predicted_data_parameters;
        } else {
          source = this.job.definition.parameters;
        }
      } else if (this.dataType.includes("actual")) {
        if ("actual_data_parameters" in this.job.definition.parameters) {
          source = this.job.definition.parameters.actual_data_parameters;
        } else {
          source = this.job.definition.parameters;
        }
      } else {
        source = this.job.definition.parameters;
      }
      console.log(this.dataType);
      console.log(source);
      if (this.dataType.includes("performance")) {
        return source.performance_granularity;
      } else {
        return source.weather_granularity;
      }
    }
  }
}
</script>
<style scoped>
span.loading-container {
  border: 0.25em solid #f3f3f3;
  border-top: 0.25em solid #3498db;
  width: 1em;
  height: 1em;
}
.file-processing-container {
  padding: 1em;
}
ul.upload-statuses {
  list-style: none;
}
#header-line,
#data-start-line {
  width: 3em;
}
label {
  display: inline-block;
}
</style>
