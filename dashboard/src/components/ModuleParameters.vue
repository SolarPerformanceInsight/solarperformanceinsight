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
      <input v-model="parameters.gamma_ref" />
      <br />
      <b>mu_gamma:</b>
      <input v-model="parameters.mu_gamma" />
      <br />
      <b>I_L_ref:</b>
      <input v-model="parameters.I_L_ref" />
      <br />
      <b>I_o_ref:</b>
      <input v-model="parameters.I_o_ref" />
      <br />
      <b>R_sh_ref:</b>
      <input v-model="parameters.R_sh_ref" />
      <br />
      <b>R_sh_0:</b>
      <input v-model="parameters.R_sh_0" />
      <br />
      <b>R_s:</b>
      <input v-model="parameters.R_s" />
      <br />
      <b>alpha_sc:</b>
      <input v-model="parameters.alpha_sc" />
      <br />
      <b>EgRef:</b>
      <input v-model="parameters.EgRef" />
      <br />
      <b>cells_in_series:</b>
      <input v-model="parameters.cells_in_series" />
      <br />
    </div>
    <div v-if="model == 'pvwatts'">
      <b>pdc0:</b>
      <input v-model="parameters.pdc0" />
      <br />
      <b>gamma_pdc:</b>
      <input v-model="parameters.gamma_pdc" />
      <br />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
// Update with many classes of inverter parameters to check for type before
// choosing a display.
import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";

@Component
export default class ModuleParametersView extends Vue {
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
