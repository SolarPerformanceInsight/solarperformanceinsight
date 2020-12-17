<!--
Maps required and optional fields to headers.
Takes the following properties
  - headers: Array<string> - An array of string headers available in the csv.
  - usedHeaders: Array<string> - An array for keeping track of headers that are
    already mapped.
  - required: Array<string> - An array of required variables to map.
  - optional: Array<string> - An array of optional fields to map.
  - comp: SystemComponent - The System, Inverter, or Array being mapped.

Components using the mapper should react to events emitted from this component:
  - free-header: payload(header: string) - Should remove the header from the
    `usedHeaders` array.
  - used-header: payload(header: string) - Should add the header to the
    `usedHeader` array.
  - mapping-updated: payload({<variable>:<header>,..., index: Array<number>) -
    Should update the master mapping with the new fields. The index property
    should be used to determine the location of the mapped System component.
-->
<template>
  <div class="csv-mapper">
    <div>
      <div class="metadata" v-if="metadata">
        <b>Name:</b>
        {{ metadata.name }}
        <br />
        <template v-if="'make_model' in metadata">
          <template v-if="'parent' in metadata">
            <b>Module Make and Model:</b>
            {{ metadata.make_model }}
            <br />
            <b>Inverter Name:</b>
            {{ metadata.parent.name }}
            <br />
            <b>Inverter Make and Model:</b>
            {{ metadata.parent.make_model }}
          </template>
          <template v-else>
            <b>Make and Model:</b>
            {{ metadata.make_model }}
            <br />
          </template>
        </template>
      </div>
      <!-- Required fields -->
      <ul class="mapping-list">
        <li v-for="field of required" :key="field">
          {{ field }} (required):
          <select @change="addMapping($event, field)">
            <option>Not included</option>
            <option
              v-for="u in headers"
              :key="u"
              :name="u"
              :disabled="usedHeaders.includes(u)"
            >
              {{ u }}
            </option>
          </select>
        </li>
      </ul>
      <!-- optional fields -->
      <ul class="mapping-list">
        <li v-for="field of optional" :key="field">
          {{ field }}:
          <select @change="addMapping($event, field)">
            <option>Not included</option>
            <option
              v-for="u in headers"
              :key="u"
              :name="u"
              :disabled="usedHeaders.includes(u)"
            >
              {{ u }}
            </option>
          </select>
        </li>
      </ul>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import FileUpload from "@/components/FileUpload.vue";
import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

const optionalFields = [
  "temp_air",
  "wind_speed",
  "cell_temperature",
  "module_temperature"
];

type SystemComponent = System | Inverter | PVArray;
type SystemComponentIndexed = SystemComponent & {
  index: Array<number>;
};

@Component
export default class FieldMapper extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() usedHeaders!: Array<string>;
  @Prop() required!: Array<string>;
  @Prop() optional!: Array<string>;
  @Prop() comp!: SystemComponentIndexed;
  @Prop() system!: StoredSystem;
  mapping!: Record<string, string>;

  data() {
    return {
      mapping: {}
    };
  }
  get metadata() {
    // If the component's index is longer than 1, we are working with an array.
    if (this.comp.index.length > 1) {
      const inverter = this.system.definition.inverters[this.comp.index[0]];
      return { ...this.comp, parent: { ...inverter } };
    } else {
      return this.comp;
    }
  }
  addMapping(event: any, variable: string) {
    const fileHeader = event.target.value;

    // If the variable is already in the mapping, free the header it is
    // currently mapped to.
    if (variable in this.mapping) {
      this.$emit("free-header", this.mapping[variable]);
    }
    if (fileHeader == "Not included") {
      // unmap the variable if not included
      delete this.mapping[variable];
    } else {
      // Update mapping and emit an event using the header.
      this.mapping[variable] = fileHeader;
      this.$emit("used-header", fileHeader);
    }
    this.$emit("mapping-updated", { ...this.mapping, index: this.comp.index });
  }
  isValid() {
    return this.required.every(x => x in this.mapping);
  }
}
</script>
<style scoped>
div.metadata {
  border: solid 1px black;
}
</style>
