<template>
  <div class="system">
    <b>Name:</b>
    <input v-model="system.name" />
    <help :helpText="this.definitions.properties.name.description" />
    <br />
    <span style="color:#F00;" v-if="'name' in this.errors">
      {{ this.errors.name }}
      <br />
    </span>
    <b>Latitude:</b>
    <input type="number" v-model.number="system.latitude" />
    <help :helpText="this.definitions.properties.latitude.description" />
    <br />
    <span style="color:#F00;" v-if="'latitude' in this.errors">
      {{ this.errors.latitude }}
      <br />
    </span>
    <b>Longitude:</b>
    <input type="number" v-model.number="system.longitude" />
    <help :helpText="this.definitions.properties.longitude.description" />
    <br />
    <span style="color:#F00;" v-if="'longitude' in this.errors">
      {{ this.errors.longitude }}
      <br />
    </span>
    <b>Elevation:</b>
    <input type="number" v-model.number="system.elevation" />
    <help :helpText="this.definitions.properties.elevation.description" />
    <br />
    <span style="color:#F00;" v-if="'elevation' in this.errors">
      {{ this.errors.elevation }}
      <br />
    </span>
    <b>Albedo:</b>
    <input type="number" v-model.number="system.albedo" />
    <help :helpText="this.definitions.properties.albedo.description" />
    <br />
    <span style="color:#F00;" v-if="'albedo' in this.errors">
      {{ this.errors.albedo }}
      <br />
    </span>
    <inverters-view :inverters="system.inverters" :model="model" />
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import HelpPopup from "@/components/Help.vue";

import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import InvertersView from "@/components/Inverters.vue";
import { System } from "@/types/System";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

Vue.component("inverters-view", InvertersView);
Vue.component("help", HelpPopup);

@Component
export default class SystemView extends ModelBase {
  @Prop() system!: System;
  @Prop() model!: string;

  components = ["inverters-view"];

  get apiComponentName() {
    return "PVSystem";
  }
  @Watch("system", { deep: true })
  validate(newSystem: Record<string, any>) {
    const system = newSystem as System;
    this.$validator
      .validate(this.apiComponentName, system)
      .then(this.setValidationResult);
  }
}
</script>

<style scoped>
div {
  text-align: left;
}
</style>
