<template>
  <li class="inverter">
    <b>System Name: </b> {{ $parent.$parent.system.name }}<br />
    <b>Name: </b><input v-model="inverter.name" /><br />
    <b>Make and Model: </b><input v-model="inverter.makeModel" /><br />
    <b>Inverter Parameters:</b><br />
    <inverter-parameters :parameters="inverter.inverterParameters" />
    <arrays-view :pvarrays="inverter.arrays" /><br />
    <button @click="removeInverter">Remove Inverter</button><br />
    <button @click="duplicateInverter">Duplicate Inverter</button>
  </li>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import InverterParametersView from "@/components/InverterParameters";
import ArraysView from "@/components/Arrays";
import { Inverter } from "@/types/Inverter";

Vue.component("arrays-view", ArraysView);
Vue.component("inverter-parameters", InverterParametersView);

@Component
export default class InverterView extends Vue {
  @Prop() inverter: Inverter;
  @Prop() index: number;

  removeInverter() {
    this.$parent.inverters.splice(this.index, 1);
  }
  duplicateInverter() {
    this.$parent.inverters.push(new Inverter(this.inverter));
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li.inverter {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
