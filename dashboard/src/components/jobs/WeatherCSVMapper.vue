<template>
  <div class="weather-csv-mapper">
    My data file includes:<br />
    <input id="complete-irradiance" value="complete-irradiance" type="radio" v-model="provided" />
    <label for="complete-irradiance">
      global horizontal (GHI), direct normal (DNI), and diffuse horizontal (DHI) irradiance.
    </label>
    <br />
    <input id="poa" value="poa" type="radio" v-model="provided" />
    <label for="poa">
      global plane of array (POA global), direct plane of array(POA direct), and diffuse plane of array(POA diffuse) irradiance.
    </label>
    <br />
    <input id="effective-irradiance" value="effective-irradiance" type="radio" v-model="provided" />
    <label for="effective-irradiance">
      effective irradiance.
    </label>
    <br />
    I have data for:<br />
    <input id="system" value="system" type="radio" v-model="dataLevel" />
    <label for="system">
      the entire system.
    </label>
    <br />
    <input id="inverter" value="inverter" type="radio" v-model="dataLevel" />
    <label for="inverter">
      each inverter.
    </label>
    <br />
    <input id="array" value="array" type="radio" v-model="dataLevel" />
    <label for="array">
      each array.
    </label>
    <br />
    <div>
      <div v-for="thing of toMap" :key="thing.name">
        <p>What fields contain data for data for {{ dataLevel }} <b>{{ thing.name }}</b>?</p>
        <!-- Required fields -->
        <ul class="mapping-list">
          <li v-for="field of required" :key="field">
           {{ field }} (required):
           <select @change="addMapping($event, field, thing.index)">
             <option>Not included</option>
             <option v-for="u in unMapped" :key="u">{{u}}</option>
           </select>
          </li>
        </ul>
        <!-- optional fields -->
        <ul class="mapping-list">
          <li v-for="field of optional" :key="field">
           {{ field }}:
           <select @change="addMapping($event, field, thing.index)">
             <option>Not included</option>
             <option v-for="u in unMapped" :key="u">{{u}}</option>
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
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

// Maps the required irradiance components to the data that the user has
const requiredFields = {
  "complete-irradiance": ["dni", "ghi", "dhi"],
  "poa": ["poa_global", "poa_direct", "poa_diffuse"],
  "effective-irradiance": ["effective_irradiance"]
};

const optionalFields = ["temp_air", "wind_speed", "cell_temperature", "module_temperature"];

@Component
export default class WeatherUpload extends Vue {
  @Prop() headers!: Array<string>;
  system!: System;
  provided!: keyof typeof requiredFields;
  mapping!: Record<string, string>;
  dataLevel!: "system" | "inverter" | "array";
  optional!: Array<string>;

  data() {
    return {
      mapping: {},
      provided: "complete-irradiance",
      optional: optionalFields,
      dataLevel: "system",
      system: new System({
        inverters: [new Inverter({
          arrays: [new PVArray({})]
        })],
      }) // TODO:pass in system
    }
  }
  get required() {
    return requiredFields[this.provided];
  }
  get unMapped() {
    const unmapped = this.headers.filter(x => !(x in this.mapping));
    console.log(unmapped);
    return unmapped;
  }
  get toMap() {
    if (this.dataLevel == "system"){
      return [{ index: [0], ...this.system }];
    } else if(this.dataLevel == "inverter"){
      return this.system.inverters.map((x, i) => {return { index: [i], ...x }});
    } else if(this.dataLevel == "array"){
      return this.system.inverters.map(
        (x, inv_i) => x.arrays.map((y, arr_i) => {
          return {
            index: [inv_i, arr_i],
            ...y
          }
        })
    ).flat();
    } else {
      throw new Error("Bad data level");
    }
  }
  addMapping(event: any, variable: string, index: Array<number> ){
    const headerField = event.target.value;
    if (headerField == "Not included") {
      if (headerField in this.mapping) {
        delete this.mapping[headerField];
      };
    }
    console.log(headerField, variable, this.dataLevel, index);
    if (this.dataLevel == "system"){
      this.mapping[headerField] = variable;
    } else if (this.dataLevel == "inverter") {
      this.mapping[headerField] = variable;
    }  else if (this.dataLevel == "array") {
      this.mapping[headerField] = variable;
    } else {
      throw new Error("Bad dataLevel in addMapping");
    }
  }
}
</script>
