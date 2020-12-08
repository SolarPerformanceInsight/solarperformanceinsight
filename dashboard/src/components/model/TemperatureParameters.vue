<template>
  <div class="temperature-parameters">
    <div v-if="model == 'pvsyst'">
      <model-field
        field-name="u_c"
        input-type="number" />
      <model-field
        field-name="u_v"
        input-type="number" />
      <model-field
        field-name="alpha_absorption"
        input-type="number" />
      <model-field
        field-name="eta_m"
        input-type="number"/>
    </div>
    <div v-if="model == 'pvwatts'">
      <model-field
        field-name="a"
        input-type="number" />
      <model-field
        field-name="b"
        input-type="number" />
      <model-field
        field-name="deltaT"
        input-type="number" />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";

// Update with many classes of inverter parameters to check for type before
// choosing a display.
import {
  PVSystTemperatureParameters,
  SAPMTemperatureParameters
} from "@/types/TemperatureParameters";


@Component
export default class TemperatureParametersView extends ModelBase {
  @Prop() parameters!: PVSystTemperatureParameters | SAPMTemperatureParameters;

  @Prop() model!: string;
  errors: Record<string, any> = {};

  get apiComponentName() {
    let componentName: string;
    if (this.model == "pvsyst") {
      componentName = "PVsystTemperatureParameters";
    } else {
      componentName = "SAPMTemperatureParameters";
    }
    return componentName;
  }

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>){
    this.$validator
      .validate(this.apiComponentName, newParams)
      .then(this.setValidationResult);
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
div.temperature-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
