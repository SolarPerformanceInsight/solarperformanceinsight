<!--
component that handles the csv headers of one file and master mapping for the
system.
Takes the following props:
  - headers: Array<string> - the csv headers to be mapped.
  - required: Array<string> - Required fields to be mapped for each component.
  - weather_granularity: string: What part of the spec the weather data is
    associated with. One of:
    - "system": System wide data in the file.
    - "inverter": Data for each inverter in the file.
    - "array": Data for each array in the file.
  - system: System: The system definition stored with the job as
    `system_definition`.

-->
<template>
  <div class="weather-csv-mapper">
    <div>
      <slot></slot>
      <div>
        <!-- Time mapping for the whole file -->
        <b>Timestamp column:</b>
        <select @change="mapTime">
          <option value="" disabled selected>
            Unmapped
          </option>
          <option
            v-for="(u, i) in headers"
            :key="u"
            :name="u"
            :value="u"
            :disabled="usedHeaders.includes(u)"
          >
            <template v-if="u == ''">column {{ i + 1 }}</template>
            <template v-else>{{ u }}</template>
          </option>
        </select>
        <template v-if="!timeMapped">
          <span class="warning-text">Required</span>
        </template>
      </div>
      <!-- Present a mapper for each System, Inverter, or Array (dependent on
           weather granularity.
        -->
      <div v-for="(component, i) of toMap" :key="i">
        <div>
          <div class="data-object-header">
            <span class="object-name">
              <b class="granularity">{{ weather_granularity }}:</b>
              {{ component.metadata.name }}
            </span>
            <span class="component-requirements">
              <!-- Text to alert user that fields need to be mapped -->
              <span class="warning" v-if="!componentValidity[refName(i)]">
                Missing Fields
              </span>
              <span v-else>
                Field Mapping Complete
              </span>
              <!-- Text to alert user that the component requires data
                   Uncomment when multi-file capability is added.
              <span
                class="component-requirement warning"
                v-if="!component.data_object.definition.present"
              >
                Requires Data
              </span>
              <template v-else>Complete</template>
              -->
            </span>
            <button
              class="data-object-expander"
              @click="
                dataObjectDisplay[refName(i)] = !dataObjectDisplay[refName(i)]
              "
              v-bind:class="{ opened: dataObjectDisplay[refName(i)] }"
            ></button>
          </div>
          <div v-if="dataObjectDisplay[refName(i)]">
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
              :comp="component"
              :required="requiredFields"
            >
              <p>
                What fields contain data for {{ weather_granularity }}
                <b>{{ component.metadata.name }}</b>
                ?
              </p>
            </field-mapper>
          </div>
        </div>
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
  @Prop() data_objects!: Array<Record<string, any>>;
  mapping!: Record<string, string>;
  componentValidity!: Record<string, boolean>;
  usedHeaders!: Array<string>;
  isValid!: boolean;
  timeField!: string;

  data() {
    return {
      mapping: {},
      componentValidity: {},
      usedHeaders: [],
      isValid: false,
      timeField: "",
      dataObjectDisplay: this.initDataObjectDisplay()
    };
  }
  get unMapped() {
    // Returns an array of headers that have yet to be mapped.
    const unmapped = this.headers.filter(x => !(x in this.mapping));
    return unmapped;
  }
  get toMap() {
    /* Create an array containing objects with a data object and metadata
     * object.
     * - data_object: Object - Data object from the api.
     * - metadata: System | Inverter | PVArray - metadata of the object
     *     to be mapped.
     */
    if (this.weather_granularity == "system") {
      return this.data_objects.map(obj => {
        return {
          data_object: obj,
          metadata: this.system
        };
      });
    } else if (this.weather_granularity == "inverter") {
      return this.data_objects.map(obj => {
        // get the second element of the location, due to "" first element
        const index = parseInt(obj.definition.schema_path.split("/")[2]);
        return {
          data_object: obj,
          metadata: this.system.inverters[index]
        };
      });
    } else {
      return this.data_objects.map(obj => {
        // splitting on "/" results in empty first element, so slice out
        const loc_array = obj.definition.schema_path.split("/").slice(1);
        const arr_index = parseInt(loc_array[loc_array.length - 1]);
        const inv_index = parseInt(loc_array[1]);
        return {
          data_object: obj,
          metadata: {
            parent: this.system.inverters[inv_index],
            ...this.system.inverters[inv_index].arrays[arr_index]
          }
        };
      });
    }
  }
  get requiredFields() {
    // Returns the list of required fields, other than 'time' to be mapped
    // for each object appropriate for the granularity
    return this.required.filter(r => r != "time");
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
    newMap["time"] = this.timeField;
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
    this.componentValidity = componentValidity;
    this.isValid =
      Object.values(componentValidity).every(x => x === true) &&
      this.timeMapped;
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
  initDataObjectDisplay() {
    const visibleMap: Record<string, boolean> = {};
    this.data_objects.map((x: any, i: number) => {
      visibleMap[this.refName(i)] = !x.definition.present;
    });
    return visibleMap;
  }
  get timeMapped() {
    return this.timeField != "";
  }
  mapTime(event: any) {
    this.freeHeader(this.timeField);
    const timeHeader = event.target.value;
    this.timeField = timeHeader;
    this.useHeader(this.timeField);
    for (const loc in this.mapping) {
      // @ts-expect-error
      this.mapping[loc]["time"] = this.timeField;
    }
    this.checkValidity();
  }
}
</script>
<style>
.data-object-header {
  border: 1px solid #444;
  padding: 0.25em;
  position: relative;
  display: flex;
}

button.data-object-expander {
  background-color: unset;
  border-bottom: 2px solid black;
  border-right: 2px solid black;
  border-top: none;
  border-left: none;
  height: 1em;
  width: 1em;
  transform: rotate(45deg);
  margin: 0 1em;
  position: absolute;
  right: 0;
  top: 25%;
  transition: transform 0.5s;
}
button.data-object-expander.opened {
  transform: rotate(225deg);
}
button.data-object-expander:hover {
  cursor: pointer;
}
button.data-object-expander:focus {
  outline: unset;
}
.expand-enter-active,
.expand-leave-active {
  transition: all 0.5s;
}
.expand-enter,
.expand-leave-to {
  height: 0px;
  opacity: 0;
}
b.granularity {
  text-transform: capitalize;
}
.component-requirements {
  display: inline-flex;
  margin-left: auto;
  margin-right: 2em;
}
.component-requirements span {
  margin: 0 0.5em;
}
</style>
