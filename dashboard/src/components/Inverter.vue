<template>
  <li>
    <b>System Name: </b> {{ $parent.$parent.system.name }}<br />
    <b>Name: </b><input v-model="inverter.name" /><br />
    <b>Make and Model: </b><input v-model="inverter.make_model" /><br />
    <b>Inverter Parameters:</b><br />
    <inverter-parameters
      :parameters="inverter.inverter_parameters"
      :model="model"
    />
    <arrays-view :pvarrays="inverter.arrays" :model="model" /><br />
    <button @click="removeInverter">Remove Inverter</button><br />
    <button @click="duplicateInverter">Duplicate Inverter</button>
  </li>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import InverterParametersView from "@/components/InverterParameters.vue";
import ArraysView from "@/components/Arrays.vue";
import { Inverter } from "@/types/Inverter";
import {
  PVSystInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

Vue.component("arrays-view", ArraysView);
Vue.component("inverter-parameters", InverterParametersView);

@Component
export default class InverterView extends Vue {
  @Prop() inverter!: Inverter;
  @Prop() index!: number;
  @Prop() model!: string;

  @Watch("model")
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.inverter.inverter_parameters = new PVSystInverterParameters();
    } else if (newModel == "pvwatts") {
      this.inverter.inverter_parameters = new PVWattsInverterParameters();
    }
  }

  removeInverter() {
    //@ts-ignore
    this.$parent.inverters.splice(this.index, 1);
  }
  duplicateInverter() {
    //@ts-ignore
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
