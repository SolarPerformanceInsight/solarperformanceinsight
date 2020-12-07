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
      <b>gamma_ref:</b>
      <input type="number" v-model.number="parameters.gamma_ref" />
      <help :helpText="this.definitions.properties.gamma_ref.description" />
      <br />
      <span style="color:#F00;" v-if="'gamma_ref' in this.errors">
        {{ this.errors.gamma_ref }}
        <br />
      </span>
      <b>mu_gamma:</b>
      <input type="number" v-model.number="parameters.mu_gamma" />
      <help :helpText="this.definitions.properties.mu_gamma.description" />
      <br />
      <span style="color:#F00;" v-if="'mu_gamma' in this.errors">
        {{ this.errors.mu_gamma }}
        <br />
      </span>
      <b>I_L_ref:</b>
      <input type="number" v-model.number="parameters.I_L_ref" />
      <help :helpText="this.definitions.properties.I_L_ref.description" />
      <br />
      <span style="color:#F00;" v-if="'I_L_ref' in this.errors">
        {{ this.errors.gamma_ref }}
        <br />
      </span>
      <b>I_o_ref:</b>
      <input type="number" v-model.number="parameters.I_o_ref" />
      <help :helpText="this.definitions.properties.I_o_ref.description" />
      <br />
      <span style="color:#F00;" v-if="'I_o_ref' in this.errors">
        {{ this.errors.I_o_ref }}
        <br />
      </span>
      <b>R_sh_ref:</b>
      <input type="number" v-model.number="parameters.R_sh_ref" />
      <help :helpText="this.definitions.properties.R_sh_ref.description" />
      <br />
      <span style="color:#F00;" v-if="'R_sh_ref' in this.errors">
        {{ this.errors.R_sh_ref }}
        <br />
      </span>
      <b>R_sh_0:</b>
      <input type="number" v-model.number="parameters.R_sh_0" />
      <help :helpText="this.definitions.properties.R_sh_0.description" />
      <br />
      <span style="color:#F00;" v-if="'R_sh_0' in this.errors">
        {{ this.errors.R_sh_0 }}
        <br />
      </span>
      <b>R_s:</b>
      <input type="number" v-model.number="parameters.R_s" />
      <help :helpText="this.definitions.properties.R_s.description" />
      <br />
      <span style="color:#F00;" v-if="'R_s' in this.errors">
        {{ this.errors.R_s }}
        <br />
      </span>
      <b>alpha_sc:</b>
      <input type="number" v-model.number="parameters.alpha_sc" />
      <help :helpText="this.definitions.properties.alpha_sc.description" />
      <br />
      <span style="color:#F00;" v-if="'alpha_sc' in this.errors">
        {{ this.errors.alpha_sc }}
        <br />
      </span>
      <b>EgRef:</b>
      <input type="number" v-model.number="parameters.EgRef" />
      <help :helpText="this.definitions.properties.EgRef.description" />
      <br />
      <span style="color:#F00;" v-if="'EgRef' in this.errors">
        {{ this.errors.EgRef }}
        <br />
      </span>
      <b>cells_in_series:</b>
      <input type="number" v-model.number="parameters.cells_in_series" />
      <help
        :helpText="this.definitions.properties.cells_in_series.description"
      />
      <br />
      <span style="color:#F00;" v-if="'cells_in_series' in this.errors">
        {{ this.errors.cells_in_series }}
        <br />
      </span>
    </div>
    <div v-if="model == 'pvwatts'">
      <b>pdc0:</b>
      <input type="number" v-model.number="parameters.pdc0" />
      <help :helpText="this.definitions.properties.pdc0.description" />
      <br />
      <span style="color:#F00;" v-if="'pdc0' in this.errors">
        {{ this.errors.pdc0 }}
        <br />
      </span>
      <b>gamma_pdc:</b>
      <input type="number" v-model.number="parameters.gamma_pdc" />
      <help :helpText="this.definitions.properties.gamma_pdc.description" />
      <br />
      <span style="color:#F00;" v-if="'gamma_pdc' in this.errors">
        {{ this.errors.gamma_pdc }}
        <br />
      </span>
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
