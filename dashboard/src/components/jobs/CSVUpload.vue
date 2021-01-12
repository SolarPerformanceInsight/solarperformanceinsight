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
  - system: StoredSystem: The system to map data onto.
  - data_objects: array - Array of data objects created by the api.
-->
<template>
  <div class="csv-upload">
  <slot>Upload your weather data</slot>
  <br />
  <label for="csv-upload">Select a file with {{ dataType }}:</label>
  <input
    id="csv-upload"
    type="file"
    accept="text/csv"
    @change="processFile"/>
    <template v-if="processingFile">
      <div class="loading-container"><div class="loading">Processing File...</div></div>
    </template>
    <template v-if="promptForMapping && !processingFile">
      <div class="warning" v-if="headers.length < totalMappings">
        Warning: It looks like you may not have enough data in this file. The
        file contains {{headers.length}} columns and {{ totalMappings }}
        columns are expected ({{ required.join(", ") }}
        for <template v-if="granularity == 'system'">the</template>
        <template v-else>each</template> {{ granularity }}).
      </div>
      <csv-mapper
        @mapping-complete="processMapping"
        @mapping-incomplete="mappingComplete=false"
        :system="system"
        :granularity="granularity"
        :data_objects="data_objects"
        :headers="headers"
        :required="required" >
        <p>Select which columns in your file contain data for the required
           variables. Data can be uploaded using the button below once the
           required variables are mapped to columns for
           {{ granularity == 'system' ? 'the system': `each ${granularity}` }}.</p>
      </csv-mapper>
      <button :disabled="!mappingComplete" @click="uploadData">Upload Data</button><span v-if="!mappingComplete">All required fields must be mapped before upload</span>
    </template>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import FileUpload from "@/components/FileUpload.vue";
import { StoredSystem } from "@/types/System";
import parseCSV from "@/utils/parseCSV";
import mapToCSV from "@/utils/mapToCSV";
import { addData } from "@/api/jobs";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}


@Component
export default class CSVUpload extends Vue {
  @Prop() jobId!: string;
  @Prop() granularity!: string;
  @Prop() irradiance_type!: string;
  @Prop() system!: StoredSystem;
  @Prop() temperature_type!: string;
  @Prop() data_objects!: Array<Record<string, any>>;
  mapping!: Record<string, Record<string, string>>;
  promptForMapping!: boolean;
  headers!: Array<string>;
  csvData!: Array<Record<string, Array<string | number>>>;
  required!: Array<string>;
  mappingComplete!: boolean;
  processingFile!: boolean;

  data() {
    return {
      mapping: {},
      processingFile: false,
      promptForMapping: false,
      headers: [],
      required: this.getRequired(),
      mappingComplete: false,
      csvData: [{}],
    }
  }
  get dataType() {
    return this.data_objects[0].definition.type;
  }
  storeCSV(csv: string) {
    // Parse the csv into an object mapping csv-headers to arrays of column
    // data.
    // TODO: parse first x lines for table to highlight mapping options
    //   during selection
    // TODO: allow for specification of header row and row where data starts
    const parsingResult = parseCSV(csv.trim());
    if (parsingResult.errors.length > 0) {
      console.log("Bad csv");
    } else {
      this.csvData = parsingResult.data;
      const headers = parsingResult.meta.fields;
      this.headers =  headers ? headers: [];
      this.processingFile = false;
      this.promptForMapping = true;
    };
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
      const fileList = e.target.files;
      const file = e.target.files[0];
      const reader = new FileReader();
      // @ts-expect-error
      reader.onload = f => this.storeCSV(f.target.result);
      reader.readAsText(file);
    }
  }
  async uploadData() {
    // function to call when all mapping has been completed. Should complete
    // the mapping process and post to the API
    for (const dataObject of this.data_objects) {
      // TODO: handle this on a single loc basis instead of looping all at once
      const loc = dataObject.definition.schema_path;
      const csv = mapToCSV(this.csvData, this.mapping[loc]);
      const token = await this.$auth.getTokenSilently();
      addData(token, this.jobId, dataObject.object_id, csv)
        .then(res => {
          console.log(`Location ${loc} uploaded.`);
        });
    }
    this.$emit("data-uploaded");
  }
  getRequired() {
    // May need to be updated if required fields are ever different for weather
    // data objects
    return this.data_objects[0].definition.data_columns;
  }
  get totalMappings() {
    return this.required.length * this.data_objects.length;
  }
}
</script>
<style scoped>
div.csv-upload {
  border: 1px solid black;
  padding: 1em;
}
</div>
