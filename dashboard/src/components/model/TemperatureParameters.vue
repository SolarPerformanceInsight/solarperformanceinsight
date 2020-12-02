<template>
  <div class="temperature-parameters">
    <div v-if="model == 'pvsyst'">
      <b>uC:</b>
      <input v-model="parameters.u_c" />
      <help :helpText="this.definitions.properties.u_c.description" />
      <br />
      <span style="color: #F00;" v-if="'u_c' in this.errors">
        {{ this.errors.u_c }}
      </span>
      <b>uV:</b>
      <input v-model="parameters.u_v" />
      <help :helpText="this.definitions.properties.u_v.description" />
      <br />
      <span style="color: #F00;" v-if="'u_v' in this.errors">
        {{ this.errors.u_v }}
      </span>
      <b>Alpha absorption:</b>
      <input v-model="parameters.alpha_absorption" />
      <help
        :helpText="this.definitions.properties.alpha_absorption.description"
      />
      <br />
      <span style="color: #F00;" v-if="'alpha_absorption' in this.errors">
        {{ this.errors.alpha_absorption }}
      </span>
      <b>eta m:</b>
      <input v-model="parameters.eta_m" />
      <help :helpText="this.definitions.properties.eta_m.description" />
      <br />
      <span style="color: #F00;" v-if="'eta_m' in this.errors">
        {{ this.errors.eta_m }}
      </span>
    </div>
    <div v-if="model == 'pvwatts'">
      <b>a:</b>
      <input v-model="parameters.a" />
      <help :helpText="this.definitions.properties.a.description" />
      <br />
      <span style="color: #F00;" v-if="'a' in this.errors">
        {{ this.errors.a }}
      </span>
      <b>b:</b>
      <input v-model="parameters.b" />
      <help :helpText="this.definitions.properties.b.description" />
      <br />
      <span style="color: #F00;" v-if="'b' in this.errors">
        {{ this.errors.b }}
      </span>
      <b>deltaT:</b>
      <input v-model="parameters.deltaT" />
      <help :helpText="this.definitions.properties.deltaT.description" />
      <br />
      <span style="color: #F00;" v-if="'deltaT' in this.errors">
        {{ this.errors.deltaT }}
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import HelpPopup from "@/components/Help.vue";

import { Component, Prop, Vue } from "vue-property-decorator";

// Update with many classes of inverter parameters to check for type before
// choosing a display.
import {
  PVSystTemperatureParameters,
  SAPMTemperatureParameters
} from "@/types/TemperatureParameters";

Vue.component("help", HelpPopup);

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
