<template>
  <div class="weather-csv-mapper">
    <div>
      <div v-for="thing of toMap" :key="thing.name">
        <p>
          What fields contain data for data for {{ weather_granularity }}
          <b>{{ thing.name }}</b>
          ?
        </p>
        <!-- Required fields -->
        <ul class="mapping-list">
          <li v-for="field of required" :key="field">
            {{ field }} (required):
            <select @change="addMapping($event, field, thing.index)">
              <option>Not included</option>
              <option v-for="u in unMapped" :key="u">{{ u }}</option>
            </select>
          </li>
        </ul>
        <!-- optional fields -->
        <ul class="mapping-list">
          <li v-for="field of optional" :key="field">
            {{ field }}:
            <select @change="addMapping($event, field, thing.index)">
              <option>Not included</option>
              <option v-for="u in unMapped" :key="u">{{ u }}</option>
            </select>
          </li>
        </ul>
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

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

// Maps the required irradiance components to the data that the user has
const requiredFields = {
  standard: ["dni", "ghi", "dhi"],
  poa: ["poa_global", "poa_direct", "poa_diffuse"],
  effective: ["effective_irradiance"]
};

const optionalFields = [
  "temp_air",
  "wind_speed",
  "cell_temperature",
  "module_temperature"
];

@Component
export default class WeatherUpload extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() weather_type!: keyof typeof requiredFields;
  @Prop() weather_granularity!: string;
  @Prop() system!: StoredSystem;
  mapping!: Record<string, string>;
  optional!: Array<string>;

  data() {
    return {
      mapping: {},
      provided: "complete-irradiance",
      optional: optionalFields
    };
  }
  get required() {
    return requiredFields[this.weather_type];
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
  addMapping(event: any, variable: string, index: Array<number>) {
    const headerField = event.target.value;
    if (headerField == "Not included") {
      if (headerField in this.mapping) {
        delete this.mapping[headerField];
      }
    }
    if (this.weather_granularity == "system") {
      this.mapping[headerField] = variable;
    } else if (this.weather_granularity == "inverter") {
      this.mapping[headerField] = variable;
    } else if (this.weather_granularity == "array") {
      this.mapping[headerField] = variable;
    } else {
      throw new Error("Bad granularity in addMapping");
    }
  }
}
</script>
