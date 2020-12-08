<template>
  <div class="module-parameters">
    <b>Parameter source:</b>
    <select v-model="parameterSource" name="module-parameter-source">
      <option>User Supplied</option>
      <option>Browse Database</option>
    </select>
    <br />
    <!-- If user selects something other than User Supplied, display the
         list of inverters from the db. This should probably be it's own
         component with some search functionality built in
     -->
    <div v-if="parameterSource !== 'User Supplied'">
      <b>Select a Module:</b>
      <select @change="loadModule" name="module-list">
        <option v-for="p in parameterOptions" :key="p">{{ p }}</option>
      </select>
      <br />
    </div>
    <div v-if="model == 'pvsyst'">
      <model-field
        field-name="gamma_ref" />
      <model-field
        field-name="mu_gamma" />
      <model-field
        field-name="I_L_ref" />
      <model-field
        field-name="I_o_ref" />
      <model-field
        field-name="R_sh_ref" />
      <model-field
        field-name="R_sh_0" />
      <model-field
        field-name="R_s" />
      <model-field
        field-name="alpha_sc" />
      <model-field
        field-name="EgRef" />
      <model-field
        field-name="cells_in_series" />
    </div>
    <div v-if="model == 'pvwatts'">
      <model-field
        field-name="pdc0" />
      <model-field
        field-name="gamma_pdc" />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";

import ModelBase from "@/components/ModelBase.vue";

import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";


@Component
export default class ModuleParametersView extends ModelBase {
  @Prop() parameters!: PVSystModuleParameters | PVWattsModuleParameters;

  @Prop({ default: "pvsyst" }) model!: string;

  @Prop({ default: null }) selectedInverter!: string;

  data() {
    return {
      parameterSource: "User Supplied"
    };
  }

  loadModule(event: Event) {
    // TODO: load inverter from correct source based on selected model.
    console.log(event.target);
  }

  get parameterOptions() {
    // Return a list of parameter options based on currently selected model
    if (this.model == "pvsyst") {
      // TODO: load pvsyst compatible parameters
      return ["PVSystModule_0", "PVSystModule_1"];
    } else if (this.model == "pvwatts") {
      // TODO: load pvwatts compatible parameters
      return ["PVWattsModule_0", "PVWattsModule_1"];
    } else {
      return [];
    }
  }

  get apiComponentName() {
    if (this.model == "pvsyst") {
      return "PVsystModuleParameters";
    } else {
      return "PVWattsModuleParameters";
    }
  }

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    let params: Record<string, any>;
    if (this.model == "pvsyst") {
      params = newParams as PVSystModuleParameters;
    } else {
      params = newParams as PVWattsModuleParameters;
    }
    this.$validator
      .validate(this.apiComponentName, params)
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
div.module-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
