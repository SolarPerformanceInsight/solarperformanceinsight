<template>
  <div class="system">
    <b>Name: </b><input v-model="system.name" /><br />
    <b>Latitude: </b><input v-model="system.latitude" /><br />
    <b>Longitude: </b><input v-model="system.longitude" /><br />
    <b>Elevation: </b><input v-model="system.elevation" /><br />
    <b>Albedo: </b><input v-model="system.albedo" /><br />
    <b>Model: </b>
    <select v-model="model">
      <option v-for="m in modelPresetOptions" :key="m">{{ m }}</option>
    </select><br />
    <a
      href="#"
      :class="displayAdvanced ? 'open' : ''"
      @click.prevent="displayAdvanced = !displayAdvanced"
    >
      Advanced
    </a>
    <div class="advanced-model-params" v-if="displayAdvanced">
      <b>Transposition Model: </b>
      <input disabled v-model="modelSpec.transposition_model" /><br />
      <b>DC Model: </b>
      <input disabled v-model="modelSpec.dc_model" /><br />
      <b>AC Model: </b>
      <input disabled v-model="modelSpec.ac_model" /><br />
      <b>AOI Model: </b>
      <input disabled v-model="modelSpec.aoi_model" /><br />
      <b>Spectral Model: </b>
      <input disabled v-model="modelSpec.spectral_model" /><br />
      <b>Temperature Model: </b>
      <input disabled v-model="modelSpec.temperature_model" /><br />
    </div>
    <inverters-view :inverters="system.inverters" :model="model" />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import InvertersView from "@/components/Inverters.vue";
import { System } from "@/types/System";
import { modelSpecs } from "@/types/ModelSpecification";

Vue.component("inverters-view", InvertersView);
@Component
export default class SystemView extends Vue {
  @Prop() system!: System;
  model!: string;

  components = ["inverters-view"];
  data() {
    return {
      model: "pvsyst",
      modelPresetOptions: ["pvsyst", "pvwatts"],
      displayAdvanced: false
    };
  }
  get modelSpec() {
    return modelSpecs[this.model];
  }
}
</script>

<style scoped>
div {
  text-align: left;
}
div.advanced-model-params {
  border: 1px solid black;
  padding: 0.5em;
  width: fit-content;
}
a::after {
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid #0000ee;
  content: "";
  position: absolute;
  margin-top: 7px;
  margin-left: 7px;
}
a.open::after {
  transform: rotate(180deg);
}
</style>
