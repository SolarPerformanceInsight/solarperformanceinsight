<template>
  <div class="temperature-parameters">
    <div v-if="model == 'pvsyst'">
      <b>uC:</b>
      <input v-model="parameters.uC" />
      <br />
      <b>uV:</b>
      <input v-model="parameters.uV" />
      <br />
    </div>
    <div v-if="model == 'pvwatts'">
      <b>a:</b>
      <input v-model="parameters.a" />
      <br />
      <b>b:</b>
      <input v-model="parameters.b" />
      <br />
      <b>deltaT:</b>
      <input v-model="parameters.deltaT" />
      <br />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
// Update with many classes of inverter parameters to check for type before
// choosing a display.
import {
  PVSystTemperatureParameters,
  PVWattsTemperatureParameters
} from "@/types/TemperatureParameters";

@Component
export default class TemperatureParametersView extends Vue {
  @Prop() parameters!:
    | PVSystTemperatureParameters
    | PVWattsTemperatureParameters;

  @Prop() model!: string;
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
