<!--
Maps required fields to headers.
Takes the following properties
  - headers: Array<string> - An array of string headers available in the csv.
  - usedHeaders: Array<string> - An array for keeping track of headers that are
    already mapped.
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
  <div class="field-mapper">
    <div>
      <div class="metadata" v-if="metadata">
        <template v-if="'make_model' in metadata">
          <template v-if="'parent' in metadata">
            <b>Module Make and Model:</b>
            {{ metadata.make_model }}
            <br />
            <template v-if="'tilt' in metadata.tracking">
              <b>Surface Tilt:</b>
              {{ metadata.tracking.tilt }}&deg;
              <br />
              <b>Surface Azimuth:</b>
              {{ metadata.tracking.azimuth }}&deg;
              <br />
            </template>
            <template v-else>
              <b>Axis Tilt:</b>
              {{ metadata.tracking.axis_tilt }}&deg;
              <br />
              <b>Axis Azimuth:</b>
              {{ metadata.tracking.axis_tilt }}&deg;
              <br />
            </template>
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
      <slot></slot>
      <!-- Required fields -->
      <ul class="mapping-list">
        <li v-for="field of required" :key="field">
          {{ getDisplayName(field) }} (required):
          <select @change="addMapping($event, field)">
            <option>Not included</option>
            <option
              v-for="(u, i) in headers"
              :key="i"
              :name="u"
              :value="u"
              :disabled="usedHeaders.includes(u)"
            >
              <template v-if="u == ''">column {{ i + 1 }}</template>
              <template v-else>
                {{ u }}
              </template>
            </option>
          </select>
        </li>
      </ul>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

interface HTMLInputEvent extends Event {
  target: HTMLInputElement & EventTarget;
}

interface MetadataWithDataObject {
  data_object: Record<string, any>;
  metadata: System | Inverter | PVArray;
}

type SystemComponent = System | Inverter | PVArray;

// Maps variables to human friendly names
const displayNames = {
  time: "Timestamp",
  ghi: "Global Horizontal Irradiance",
  dhi: "Diffuse Horizontal Irradiance",
  dni: "Direct Normal Irradiance",
  poa_global: "Plane of Array Global Irradiance",
  poa_diffuse: "Plane of Array Diffuse Irradiance",
  poa_direct: "Plane of Array Direct Irradiance",
  effective_irradiance: "Effective Irradiance",
  cell_temperature: "Cell Temperature",
  module_temperature: "Module Temperature",
  temp_air: "Air Temperature",
  wind_speed: "Wind Speed",
  performance: "Performance (AC power)"
};

@Component
export default class FieldMapper extends Vue {
  @Prop() headers!: Array<string>;
  @Prop() usedHeaders!: Array<string>;
  @Prop() comp!: MetadataWithDataObject;
  mapping!: Record<string, string>;

  data() {
    return {
      mapping: {}
    };
  }
  get metadata() {
    return this.comp.metadata;
  }
  get required() {
    // return all required fields besides time, which is mapped at the
    // file level
    return this.comp.data_object.definition.data_columns.filter(
      (x: string) => x != "time"
    );
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
    this.$emit("mapping-updated", {
      ...this.mapping,
      loc: this.comp.data_object.definition.schema_path
    });
  }
  getDisplayName(variable: string) {
    // @ts-expect-error
    return displayNames[variable];
  }
  isValid() {
    return this.required.every((x: string) => x in this.mapping);
  }
}
</script>
<style scoped>
div.metadata {
}
.mapping-list li {
  margin-top: 0.5em;
}
.field-mapper {
  padding-left: 1em;
}
</style>
