<!--
component that handles the csv headers of one file and master mapping for the
system.
Takes the following props:
  - headers: Array<string> - the csv headers to be mapped.
  - granularity: string: What part of the spec the data is
    associated with. One of:
    - "system": System wide data in the file.
    - "inverter": Data for each inverter in the file.
    - "array": Data for each array in the file.
  - system: System: The system definition stored with the job as
    `system_definition`.

-->
<template>
  <div class="csv-mapper">
    <div>
      <slot></slot>
      <div>
        <!-- Time mapping for the whole file -->
        <b>
          <template v-if="indexField == 'time'">
            Timestamp
          </template>
          <template v-else>
            Month
          </template>
          column:
        </b>
        <select @change="mapIndex">
          <option @mouseover="fireSelect(null)" value="" disabled selected>
            Unmapped
          </option>
          <option
            @mouseover="fireSelect(u)"
            v-for="(u, i) in headers"
            :key="i"
            :name="u"
            :value="u"
            :disabled="usedHeaders.includes(u)"
          >
            <template v-if="u == ''">column {{ i + 1 }}</template>
            <template v-else>{{ u }}</template>
          </option>
        </select>
        <template v-if="!indexMapped">
          <span class="warning-text">Required</span>
        </template>
      </div>
      <!-- Present a mapper for each System, Inverter, or Array (dependent on
           granularity.
        -->
      <div v-for="(component, i) of toMap" :key="i">
        <div>
          <div class="data-object-header">
            <span class="object-name">
              <b class="granularity">{{ granularity }}:</b>
              {{ component.metadata.name }}
            </span>
            <span class="component-requirements">
              <!-- Text to alert user that fields need to be mapped -->
              <span class="warning" v-if="!componentValidity[refName(i)]">
                Missing Fields
              </span>
              <span v-else>
                Ready for Upload
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
          <div>
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
              :indexField="indexField"
              :comp="component"
              :show="dataObjectDisplay[refName(i)]"
            >
              <p>
                What fields contain data for {{ granularity }}
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
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { System } from "@/types/System";
import FieldMapper from "@/components/jobs/FieldMapper.vue";
interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}
Vue.component("field-mapper", FieldMapper);

@Component
export default class CSVMapper extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() granularity!: string;
  @Prop() system!: System;
  @Prop() data_objects!: Array<Record<string, any>>;
  @Prop() indexField!: string;
  mapping!: Record<string, string>;
  componentValidity!: Record<string, boolean>;
  usedHeaders!: Array<string>;
  isValid!: boolean;
  indexHeader!: string;

  data() {
    return {
      mapping: {},
      componentValidity: {},
      usedHeaders: [],
      isValid: false,
      indexHeader: "",
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
    if (this.granularity == "system") {
      return this.data_objects.map(obj => {
        return {
          data_object: obj,
          metadata: this.system
        };
      });
    } else if (this.granularity == "inverter") {
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
  get required() {
    return this.data_objects[0].definition.data_columns;
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
    newMap[this.indexField] = { csv_header: this.indexHeader };
    delete newMap["loc"];
    this.mapping[loc] = newMap;
    this.checkValidity();
    this.emitMapping();
  }
  emitMapping() {
    const mapObject = {
      mapping: this.mapping,
      complete: false
    };
    if (this.isValid) {
      mapObject.complete = true;
    }
    this.$emit("new-mapping", mapObject);
  }
  checkValidity() {
    // Check that all child components are completely mapped.
    const componentValidity: Record<string, boolean> = {};

    for (const ref in this.$refs) {
      // @ts-expect-error
      componentValidity[ref] = this.$refs[ref][0].isValid();
    }
    this.componentValidity = componentValidity;
    this.isValid =
      Object.values(componentValidity).every(x => x === true) &&
      this.indexMapped;
  }
  refName(index: number) {
    // Create a unique ref name for a nested component. Used to store
    // references to nested components for checking that all mappings are
    // valid and complete.
    return `${this.granularity}_${index}`;
  }
  initDataObjectDisplay() {
    const visibleMap: Record<string, boolean> = {};
    this.data_objects.map((x: any, i: number) => {
      visibleMap[this.refName(i)] = !x.definition.present;
    });
    return visibleMap;
  }
  get indexMapped() {
    return this.indexHeader != "";
  }
  mapIndex(event: any) {
    this.freeHeader(this.indexField);
    const indexHeader = event.target.value;
    this.indexHeader = indexHeader;
    this.useHeader(this.indexHeader);
    for (const dataObject of this.data_objects) {
      const loc = dataObject.definition.schema_path;
      const indexMapping = { csv_header: this.indexHeader };
      // update the index field or create a mapping
      if (loc in this.mapping) {
        // @ts-expect-error
        this.mapping[loc][this.indexField] = indexMapping;
      } else {
        const fieldMapping: Record<string, Record<string, string>> = {};
        fieldMapping[this.indexField] = indexMapping;
        // @ts-expect-error
        this.mapping[loc] = fieldMapping;
      }
    }
    this.checkValidity();
    this.emitMapping();
  }
  fireSelect(selected: string | null) {
    this.$emit("option-hovered", selected);
  }
  @Watch("headers", { deep: true })
  resetMapping() {
    this.indexHeader = "";
    this.usedHeaders = [];
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
