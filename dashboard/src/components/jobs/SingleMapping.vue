<!--
Maps a single field to a file header .
Takes the following properties
  - variable: string - the variable being mapped
  - headers: Array<string> - An array of string headers available in the csv.
  - usedHeaders: Array<string> - An array for keeping track of headers that are
    already mapped.

Components using the mapper should react to events emitted from this component:
  - new-mapping: {
      variable: The variable being mapped,
      header: The header from the csv mapped to the variable,
      units(if power variable): Units of the power measurement.
    } - Should remove the variable property and include in the mapping.
-->
<template>
  <div class="single-mapping">
    <select @change="emitMapping" v-model="selected">
      <option>Not included</option>
      <option
        v-for="(header, i) in headers"
        :key="i"
        :name="header.header"
        :value="header"
        :disabled="usedHeaders.includes(header.header_index)"
      >
        <template v-if="header.header">{{ header.header }}</template>
        <template v-else>Column {{ i + 1 }}</template>
      </option>
    </select>
    <div v-if="isPower" class="power-units">
      <label>Units:</label>
      <select v-model="units" @change="emitMapping">
        <option value="W">W</option>
        <option value="kW">kW</option>
        <option value="MW">MW</option>
        <option value="GW">GW</option>
      </select>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { CSVHeader } from "@/utils/mapToCSV";

@Component
export default class SingleMapping extends Vue {
  @Prop() variable!: string;
  @Prop() headers!: Array<CSVHeader>;
  @Prop() usedHeaders!: Array<number>;
  selected!: string;
  units!: string;

  data() {
    return {
      selected: "Not included",
      units: "W"
    };
  }
  get isPower() {
    return this.variable.includes("performance");
  }
  emitMapping() {
    const mapping = {
      variable: this.variable,
      csv_header: this.selected
    };
    if (this.isPower) {
      // @ts-expect-error
      mapping.units = this.units;
    }
    this.$emit("new-mapping", mapping);
  }
  @Watch("headers")
  reset() {
    this.selected = "Not included";
    this.units = "W";
  }
}
</script>
<style scoped>
div.single-mapping,
div.power-units {
  display: inline-block;
}
</style>
