<!--
Component that handles upload and extracting of headers for a single file.
Takes the following props that can be extracted from job metadata.
  - temperature_type: string - the source of module temperature. One of:
    - "module": requires that "module_temperature" be provided in the file.
    - "cell": requires that "cell_temperature" be provided in the file.
    - "air": requires that "temp_air" and "wind_speed" be provided".
  - irradiance_type: string - Type of irradiance found in weather data. One of:
    - "standard": requires "ghi", "dni", and "dhi" provided in the file.
    - "poa": requires "poa_global", "poa_direct", and "poa_diffuse" provided in
      the file.
    - "effictive_irradiance": required "effective_irradiance" provided in the
      file.
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
    <label for="header-line">CSV headers are on line:</label>
    <input
      :disabled="processingFile || promptForMapping"
      id="header-line"
      type="number"
      step="1"
      min="1"
      @change="enforceDataStartOrder"
      v-model.number="headerLine"
    />
    <br />
    <label for="data-start-line">Data begins on line:</label>
    <input
      :disabled="processingFile || promptForMapping"
      id="data-start-line"
      type="number"
      step="1"
      :min="headerLine + 1"
      v-model.number="dataStartLine"
    />
    <br />
    <label for="csv-upload">Select a file with {{ dataType }}:</label>
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
    <template v-if="processingErrors">
      <div class="warning">
        Errors encountered processing your csv.
        <ul>
          <li v-for="(error, i) of processingErrors" :key="i">
            <b>{{ error.type }}</b>
            : {{ error.message }}
          </li>
        </ul>
      </div>
    </template>
    <transition name="fade">
      <div v-if="promptForMapping && !processingFile">
        <csv-mapper
          @mapping-complete="processMapping"
          @mapping-incomplete="mappingComplete = false"
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
import mapToCSV from "@/utils/mapToCSV";
import { indexSystemFromSchemaPath } from "@/utils/schemaIndexing";
import { addData } from "@/api/jobs";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

@Component
export default class CSVUpload extends Vue {
  @Prop() jobId!: string;
  @Prop() granularity!: string;
  @Prop() irradiance_type!: string;
  @Prop() system!: System;
  @Prop() temperature_type!: string;
  @Prop() data_objects!: Array<Record<string, any>>;
  mapping!: Record<string, Record<string, string>>;
  promptForMapping!: boolean;
  headers!: Array<string>;
  csvData!: Array<Record<string, Array<string | number>>>;
  required!: Array<string>;
  mappingComplete!: boolean;

  processingFile!: boolean;
  processingErrors!: Record<string, any>;
  headerLine!: number;
  dataStartLine!: number;

  uploadingData!: boolean;
  uploadStatuses!: Record<string, any>;

  data() {
    return {
      mapping: {},
      processingFile: false,
      processingErrors: null,
      promptForMapping: false,
      headers: [],
      required: this.getRequired(),
      mappingComplete: false,
      csvData: [{}],
      uploadingData: false,
      uploadStatuses: {},
      headerLine: 1,
      dataStartLine: 2
    };
  }
  get dataType() {
    return this.data_objects[0].definition.type;
  }
  storeCSV(csv: string) {
    // Parse the csv into an object mapping csv-headers to arrays of column
    // data.
    if (!(this.headerLine == 1 && this.dataStartLine == 2)) {
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
      for (linesRead; linesRead < this.dataStartLine; linesRead++) {
        csv = csv.substring(csv.indexOf(lineSep) + lineSep.length);
      }
      csv = headerString + lineSep + csv;
    }
    const parsingResult = parseCSV(csv.trim());
    if (parsingResult.errors.length > 0) {
      console.log(parsingResult.errors);
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
      this.processingErrors = errors;
    } else {
      const headers = parsingResult.meta.fields;
      if (headers && headers.length < this.totalMappings) {
        // Handle case where CSV is parsable but does not contain enough data
        this.processingErrors = {
          0: {
            type: "Too Few Columns",
            message: `You do not have enough data in this file. The file contains
${headers ? headers.length : 0} columns and ${
              this.totalMappings
            } columns are expected (one
time column, and ${this.required.filter(x => x != "time").join(", ")} for
${this.granularity == "system" ? "the" : "each"} ${this.granularity}).`
          }
        };
      } else {
        this.csvData = parsingResult.data;
        this.headers = headers ? headers : [];
        this.promptForMapping = true;
      }
    }
    this.processingFile = false;
  }
  processMapping(newMapping: Record<string, Record<string, string>>) {
    // Handle a new mapping from the CSVMapper component, this is a
    // complete mapping, so set mappingComplete to true to enable upload
    // button.
    this.mapping = newMapping;
    this.mappingComplete = true;
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
      const csv = mapToCSV(this.csvData, this.mapping[loc]);
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
      //this.$emit("data-uploaded");
    }
  }
  getRequired() {
    // May need to be updated if required fields are ever different for weather
    // data objects
    return this.data_objects[0].definition.data_columns;
  }
  get totalMappings() {
    const nonTimeRequired = this.required.filter(x => x != "time");
    return 1 + nonTimeRequired.length * this.data_objects.length;
  }
  enforceDataStartOrder() {
    if (this.headerLine >= this.dataStartLine) {
      this.dataStartLine = this.headerLine + 1;
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
</style>
