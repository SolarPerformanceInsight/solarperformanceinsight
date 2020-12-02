<template>
  <div class="arrays">
    <div class="arrays-list">
      <h2>Arrays</h2>
      <button @click="addArray">Add Array</button>
      <div class="msg warning" v-if="pvarrays.length == 0">
        Inverter requires at least one array.
      </div>
      <ul>
        <array-view
          class="array"
          v-for="(pvarray, index) in pvarrays"
          :key="index"
          :index="index"
          :pvarray="pvarray"
          :model="model"
        />
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import ArrayView from "@/components/Array.vue";
import { PVArray } from "@/types/PVArray";
import {
  PVWattsModuleParameters,
  PVSystModuleParameters
} from "@/types/ModuleParameters";
import {
  SAPMTemperatureParameters,
  PVSystTemperatureParameters
} from "@/types/TemperatureParameters";

Vue.component("array-view", ArrayView);

@Component
export default class ArraysView extends Vue {
  @Prop() pvarrays!: Array<PVArray>;
  @Prop() model!: string;

  addArray() {
    let modParamClass: any = PVWattsModuleParameters;
    let tempParamClass: any = SAPMTemperatureParameters;
    if (this.model == "pvsyst") {
      modParamClass = PVSystModuleParameters;
      tempParamClass = PVSystTemperatureParameters;
    }
    this.pvarrays.push(
      new PVArray({
        module_parameters: new modParamClass({}),
        temperature_model_parameters: new tempParamClass({})
      })
    );
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
