<!--
Component that handles the csv headers of one file and master mapping for the
system.
Takes the following props:
  - headers: Array<string> - the csv headers to be mapped.
  - required: Array<string> - Required fields to be mapped for each component.
  - optional: Array<string> - Optional fields to be mapped for each component.
    - "module": requires that "module_temperature" be provided in the file.
    - "cell": requires that "cell_temperature" be provided in the file.
    - "air": requires that "temp_air" and "wind_speed" be provided".
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
          <b>{{ thing.metadata.name }}</b>
          ?
        </p>
        <!-- ref argument here is used to determine if the mapping is complete
             (all objects have all required fields mapped).
        -->
        <field-mapper
          :ref="refName(i)"
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
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import FieldMapper from "@/components/jobs/FieldMapper.vue";
interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}
Vue.component("field-mapper", FieldMapper);

@Component
export default class WeatherCSVMapper extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() weather_granularity!: string;
  @Prop() system!: System;
  @Prop() required!: Array<string>;
  @Prop() optional!: Array<string>;
  @Prop() data_objects!: Array<Record<string, any>>;
  mapping!: Record<string, string>;
  usedHeaders!: Array<string>;
  isValid!: boolean;

  data() {
    return {
      mapping: {},
      usedHeaders: [],
      isValid: false
    };
  }
  get unMapped() {
    const unmapped = this.headers.filter(x => !(x in this.mapping));
    return unmapped;
  }
  get toMap() {
    /* Create an array containing objects with a loc string and metadata
     * object.
     * - loc: string - path of the object relative to System root.
     * - metadata: System | Inverter | PVArray - metadata of the object
     *     to be mapped.
     */
    if (this.weather_granularity == "system") {
      return this.data_objects.map(obj => {
        return {
          loc: obj.schema_path,
          metadata: this.system
        };
      });
    } else if (this.weather_granularity == "inverter") {
      return this.data_objects.map(obj => {
        // get the second element of the location, due to "" first element
        const index = parseInt(obj.schema_path.split("/")[2]);
        return {
          loc: obj.schema_path,
          metadata: this.system.inverters[index]
        };
      });
    } else {
      return this.data_objects.map(obj => {
        // splitting on "/" results in empty first element, so slice out
        const loc_array = obj.schema_path.split("/").slice(1);
        const arr_index = parseInt(loc_array[loc_array.length - 1]);
        const inv_index = parseInt(loc_array[1]);
        return {
          loc: obj.schema_path,
          metadata: {
            parent: this.system.inverters[inv_index],
            ...this.system.inverters[inv_index].arrays[arr_index]
          }
        };
      });
    }
  }
  useHeader(header: string) {
    this.usedHeaders.push(header);
  }
  freeHeader(header: string) {
    this.usedHeaders.splice(this.usedHeaders.indexOf(header), 1);
  }
  updateMapping(newMap: any) {
    // pop the index from the mapping
    const loc = newMap.loc;
    newMap = { ...newMap };
    delete newMap["loc"];
    this.mapping[loc] = newMap;
    this.checkValidity();
  }
  checkValidity() {
    // Check that all child components are completely mapped.
    // emits a "mapping-complete" event with the full mapping if valid.
    const componentValidity: Record<string, boolean> = {};

    for (const ref in this.$refs) {
      // @ts-expect-error
      componentValidity[ref] = this.$refs[ref][0].isValid();
    }
    this.isValid = Object.values(componentValidity).every(x => x === true);
    if (this.isValid) {
      this.$emit("mapping-complete", this.mapping);
    } else {
      this.$emit("mapping-incomplete");
    }
  }
  refName(index: number) {
    // Create a unique ref name for a nested component. Used to store
    // references to nested components for checking that all mappings are
    // valid and complete.
    return `${this.weather_granularity}_${index}`;
  }
}
</script>
