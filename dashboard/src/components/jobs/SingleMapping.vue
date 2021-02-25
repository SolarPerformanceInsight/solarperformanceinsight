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
      csv_header: The header from the csv mapped to the variable,
      units(if power variable): Units of the power measurement.
    } - Should remove the variable property and include in the mapping.
-->
<template>
  <div class="single-mapping">
    <select @change="emitMapping" v-model="selected">
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

@Component
export default class SingleMapping extends Vue {
  @Prop() variable!: string;
  @Prop() headers!: Array<string>;
  @Prop() usedHeaders!: Array<string>;
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
