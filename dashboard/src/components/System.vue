<template>
  <div class="system">
    <b>Name: </b><input v-model="system.name" /><br />
    <b>Latitude: </b><input v-model="system.latitude" /><br />
    <b>Longitude: </b><input v-model="system.longitude" /><br />
    <b>Elevation: </b><input v-model="system.elevation" /><br />
    <b>Albedo: </b><input v-model="system.albedo" /><br />
    <inverters-view :inverters="system.inverters" />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import InvertersView from "@/components/Inverters";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";

Vue.component("inverters-view", InvertersView);
@Component
export default class SystemView extends Vue {
  @Prop({ default: new System() }) system: System;
  components = ["inverters-view"];
}
</script>

<style scoped>
div {
  text-align: left;
}
</style>
