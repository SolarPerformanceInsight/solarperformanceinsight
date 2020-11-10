<template>
  <div class="system">
    <b>Name: </b><input v-model="system.name" /><br />
    <b>Latitude: </b><input v-model="system.latitude" /><br />
    <b>Longitude: </b><input v-model="system.longitude" /><br />
    <b>Elevation: </b><input v-model="system.elevation" /><br />
    <b>Albedo: </b><input v-model="system.albedo" /><br />
    <b>Model: </b>
    <select v-model="model">
      <option v-for="m in modelOptions" :key="m">{{ m }}</option>
    </select>
    <inverters-view :inverters="system.inverters" :model="model" />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import InvertersView from "@/components/Inverters.vue";
import { System } from "@/types/System";

Vue.component("inverters-view", InvertersView);
@Component
export default class SystemView extends Vue {
  @Prop() system!: System;
  //@Prop({default: 'pvsyst'}) model: str;

  components = ["inverters-view"];

  data() {
    return {
      model: "pvsyst",
      modelOptions: ["pvsyst", "pvwatts"]
    };
  }
}
</script>

<style scoped>
div {
  text-align: left;
}
</style>
