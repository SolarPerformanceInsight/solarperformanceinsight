<template>
  <li class="array">
    <b>Inverter Name: </b> {{ $parent.$parent.inverter.name }} <br />
    <b>Name: </b><input v-model="pvarray.name" /><br />
    <b>Make and Model: </b><input v-model="pvarray.make_model" /><br />
    <b>Module Parameters: </b><br />
    <b>Tracking: </b>
    <input v-model="tracking" type="radio" value="fixed" />Fixed
    <input type="radio" v-model="tracking" value="singleAxis" />Single Axis
    <tracking-parameters :tracking="tracking" :parameters="pvarray.tracking" />
    <module-parameters-view
      :parameters="pvarray.module_parameters"
      :model="model"
    />
    <button @click="removeArray">Remove Array</button><br />
    <button @click="duplicateArray">Duplicate Array</button>
  </li>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import { PVArray } from "@/types/PVArray";
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";

import ModuleParametersView from "@/components/ModuleParameters.vue";
import TrackingParametersView from "@/components/TrackingParameters.vue";

Vue.component("module-parameters-view", ModuleParametersView);
Vue.component("tracking-parameters", TrackingParametersView);

@Component
export default class ArrayView extends Vue {
  @Prop() pvarray!: PVArray;
  @Prop() index!: number;
  @Prop() model!: string;

  data() {
    return {
      tracking: "fixed"
    };
  }
  @Watch("model")
  changeModel(newModel: string) {
    if (newModel == "pvsyst") {
      this.pvarray.module_parameters = new PVSystModuleParameters();
    } else if (newModel == "pvwatts") {
      this.pvarray.module_parameters = new PVWattsModuleParameters();
    }
  }

  removeArray() {
    //@ts-ignore
    this.$parent.pvarrays.splice(this.index, 1);
  }
  duplicateArray() {
    //@ts-ignore
    this.$parent.pvarrays.push(new PVArray(this.pvarray));
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li.array {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
