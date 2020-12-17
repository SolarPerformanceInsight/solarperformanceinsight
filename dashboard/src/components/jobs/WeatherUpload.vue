<!--
Component that handles upload and extracting of headers for a single file.
Takes the following props that can be extracted from job metadata.
  - temperature: string - the source of module temperature. One of:
    - "module": requires that "module_temperature" be provided in the file.
    - "cell": requires that "cell_temperature" be provided in the file.
    - "air": requires that "temp_air" and "wind_speed" be provided".
  - weather_type: string - Type of irradiance found in weather data. One of:
    - "standard": requires "ghi", "dni", and "dhi" provided in the file.
    - "poa": requires "poa_global", "poa_direct", and "poa_diffuse" provided in
      the file.
    - "effictive_irradiance": required "effective_irradiance" provided in the
      file.
  - weather_granularity: string: What part of the spec the weather data is
    associated with. One of:
    - "system": System wide data in the file.
    - "inverter": Data for each inverter in the file.
    - "array": Data for each array in the file.
  - system: StoredSystem: The system to map data onto.
-->
<template>
  <div class="weather-upload">
  <slot>Upload your weather data</slot>
  <br />
  <label for="weather-upload">Select a weather file:</label>
  <input
    id="weather-upload"
    type="file"
    accept="text/csv"
    @change="processFile"/>
    <template v-if="promptForMapping">
      <div class="warning" v-if="headers.length < totalMappings">
        Warning: It looks like you may not have enough data in this file. The
        file contains {{headers.length}} columns and {{ totalMappings }}
        columns are expected (a timestamp column and {{ required.join(", ") }}
        for <template v-if="weather_granularity == 'system'">the</template>
        <template v-else>each</template> {{ weather_granularity }}).
      </div>
      <weather-csv-mapper
        :temperature="temperature"
        :system="system"
        :weather_granularity="weather_granularity"
        :weather_type="weather_type"
        :headers="headers"
        :required="required"
        :optional="optional" />
    </template>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import FileUpload from "@/components/FileUpload.vue";
import { StoredSystem } from "@/types/System";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

// Maps the required irradiance components to the data that the user has
const requiredIrradianceFields = {
  standard: ["dni", "ghi", "dhi"],
  poa: ["poa_global", "poa_direct", "poa_diffuse"],
  effective: ["effective_irradiance"]
};
const requiredTemperatureFields = {
  cell: ["cell_temperature"],
  module: ["module_temperature"],
  air: ["temp_air", "wind_speed"]
};

const optionalFields = [
  "temp_air",
  "wind_speed",
  "cell_temperature",
  "module_temperature"
];

@Component
export default class WeatherUpload extends Vue {
  @Prop() weather_granularity!: string;
  @Prop() weather_type!: string;
  @Prop() system!: StoredSystem;
  @Prop() temperature!: string;
  mapping!: Record<string, string>;
  promptForMapping!: boolean;
  headers!: Array<string>;
  required!: Array<string>;

  data() {
    return {
      mapping: {},
      promptForMapping: false,
      headers: [],
      required: this.getRequired()
    }
  }
  mapAndStoreCSV(csv: string) {
    if (csv.indexOf("\n")){
      this.headers = csv.slice(0, csv.indexOf("\n")).split(",");
      this.promptForMapping = true;;
    } else {
      console.log("Bad csv");
    }
  }
  processMapping(newMapping: Record<string, string>) {
    this.mapping = newMapping;
  }
  processFile(e: HTMLInputEvent) {
    if (e.target.files !== null) {
      const fileList = e.target.files;
      const file = e.target.files[0];
      const reader = new FileReader();
      // @ts-expect-error
      reader.onload = f => this.mapAndStoreCSV(f.target.result);
      reader.readAsText(file);
    }
  }
  getRequired() {
    let requiredFields: Array<string> = ["time"];
    requiredFields = requiredFields.concat(
      //@ts-expect-error
      requiredIrradianceFields[this.weather_type].concat(
        // @ts-expect-error
        requiredTemperatureFields[this.temperature]
      )
    );
    return requiredFields;
  }
  get optional() {
    return optionalFields.filter(x => !this.required.includes(x));
  }
  get totalMappings() {
    // number of required variables plus one for timestamps.
    let total: number;
    const numRequired = this.required.length;
    if (this.weather_granularity == "system") {
      total = numRequired;
    } else if (this.weather_granularity == "inverter") {
      const numInverters = this.system.definition.inverters.length;
      total = numRequired * numInverters;
    } else {
      const numArrays = this.system.definition.inverters.reduce(
        (totalArrays: number, inverter) => {
           return totalArrays + inverter.arrays.length
        },
        0
      );
      total = numRequired * numArrays;
    }
    return total;
  }
}
</script>
<style scoped>
div.weather-upload {
  border: 1px solid black;
  padding: 1em;
}
</div>
