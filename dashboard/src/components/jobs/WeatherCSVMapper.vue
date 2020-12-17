<!--
Component that handles the csv headers of one file and master mapping for the
system.
Takes the following props:
  - headers: Array<string> - the csv headers to be mapped.
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
  <div class="weather-csv-mapper">
    <div>
      <div v-for="(thing, i) of toMap" :key="i">
        <p>
          What fields contain data for data for {{ weather_granularity }}
          <b>{{ thing.name }}</b>
          ?
        </p>
        <field-mapper
          @used-header="useHeader"
          @free-header="freeHeader"
          @mapping-updated="updateMapping"
          :headers="headers"
          :usedHeaders="usedHeaders"
          :comp="thing"
          :system="system"
          :required="required"
          :optional="optional"
        />
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import FileUpload from "@/components/FileUpload.vue";
import { StoredSystem } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import FieldMapper from "@/components/jobs/FieldMapper.vue";
interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}
Vue.component("field-mapper", FieldMapper);
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
export default class WeatherCSVMapper extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() temperature!: string;
  @Prop() weather_type!: string;
  @Prop() weather_granularity!: string;
  @Prop() system!: StoredSystem;
  mapping!: Record<string, string>;
  required!: Array<string>;
  usedHeaders!: Array<string>;

  data() {
    return {
      mapping: {},
      required: this.getRequired(),
      usedHeaders: []
    };
  }
  getRequired() {
    let requiredFields: Array<string> = [];
    // @ts-expect-error
    requiredFields = requiredIrradianceFields[this.weather_type].concat(
      // @ts-expect-error
      requiredTemperatureFields[this.temperature]
    );
    return requiredFields;
  }
  get optional() {
    return optionalFields.filter(x => !this.required.includes(x));
  }
  get unMapped() {
    const unmapped = this.headers.filter(x => !(x in this.mapping));
    console.log(unmapped);
    return unmapped;
  }
  get toMap() {
    if (this.weather_granularity == "system") {
      return [{ index: [0], ...this.system.definition }];
    } else if (this.weather_granularity == "inverter") {
      return this.system.definition.inverters.map((x, i) => {
        return { index: [i], ...x };
      });
    } else if (this.weather_granularity == "array") {
      return this.system.definition.inverters
        .map((x, inv_i) =>
          x.arrays.map((y, arr_i) => {
            return {
              index: [inv_i, arr_i],
              ...y
            };
          })
        )
        .flat();
    } else {
      throw new Error("Bad data level");
    }
  }
  useHeader(header: string) {
    this.usedHeaders.push(header);
  }
  freeHeader(header: string) {
    this.usedHeaders.splice(this.usedHeaders.indexOf(header), 1);
  }
  updateMapping(newMap: any) {
    const index = newMap.index;
    delete newMap.index;
    let loc: string;
    if (this.weather_granularity == "system") {
      loc = "/"; // system/definition?
    } else if (this.weather_granularity == "inverter") {
      loc = "/inverters/index[0]";
    } else if (this.weather_granularity == "array") {
      loc = "/inverters/[index[0]/arrays/index[2]";
    } else {
      throw new Error("Bad granularity in updateMapping");
    }
    this.mapping[loc] = newMap;
  }
}
</script>
