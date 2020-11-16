<template>
  <li>
    <b>Inverter Name: </b> {{ $parent.$parent.inverter.name }} <br />
    <b>Name: </b><input v-model="pvarray.name" /><br />
    <b>Make and Model: </b><input v-model="pvarray.make_model" /><br />
    <b>Tracking: </b>
    <input v-model="tracking" type="radio" value="fixed" />Fixed
    <input type="radio" v-model="tracking" value="singleAxis" />Single Axis
    <tracking-parameters :tracking="tracking" :parameters="pvarray.tracking" />
    <b>Temperature Model Parameters:</b><br />
    <temperature-parameters
      :model="model"
      :parameters="pvarray.temperature_model_parameters"
    />
    <b>Module Parameters: </b><br />
    <module-parameters :parameters="pvarray.module_parameters" :model="model" />
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

import {
  PVSystTemperatureParameters,
  PVWattsTemperatureParameters
} from "@/types/TemperatureParameters";

import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";

import ModuleParametersView from "@/components/ModuleParameters.vue";
import TrackingParametersView from "@/components/TrackingParameters.vue";
import TemperatureParametersView from "@/components/TemperatureParameters.vue";

Vue.component("module-parameters", ModuleParametersView);
Vue.component("tracking-parameters", TrackingParametersView);
Vue.component("temperature-parameters", TemperatureParametersView);

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
      this.pvarray.temperature_model_parameters = new PVSystTemperatureParameters();
    } else if (newModel == "pvwatts") {
      this.pvarray.module_parameters = new PVWattsModuleParameters();
      this.pvarray.temperature_model_parameters = new PVWattsTemperatureParameters();
    }
  }
  @Watch("tracking")
  changeTracking(tracking: string) {
    if (tracking == "fixed") {
      this.pvarray.tracking = new FixedTrackingParameters();
    } else {
      this.pvarray.tracking = new SingleAxisTrackingParameters();
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
