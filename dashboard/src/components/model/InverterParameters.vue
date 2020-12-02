<template>
  <div class="inverter-parameters">
    <b>Parameter source:</b>
    <select v-model="parameterSource" name="parameter-source">
      <option>User Supplied</option>
      <option>Browse Database</option>
    </select>
    <br />
    <!-- If user selects something other than User Supplied, display the
         list of inverters from the db. This should probably be it's own
         component with some search functionality built in
     -->
    <div v-if="parameterSource !== 'User Supplied'">
      <b>Select an Inverter:</b>
      <select @change="loadInverter" name="inverter-list">
        <option v-for="p in parameterOptions" :key="p">{{ p }}</option>
      </select>
      <br />
    </div>
    <div v-if="model == 'pvsyst'">
      <b>AC Power Rating:</b>
      <input type="number" v-model.number="parameters.Paco" />
      <help :helpText="this.definitions.properties.Paco.description" />
      <br />
      <span style="color:#F00;" v-if="'Paco' in this.errors">
        {{ this.errors.Paco }}
        <br />
      </span>
      <b>DC Power Rating:</b>
      <input type="number" v-model.number="parameters.Pdco" />
      <help :helpText="this.definitions.properties.Pdco.description" />
      <br />
      <span style="color:#F00;" v-if="'Pdco' in this.errors">
        {{ this.errors.Pdco }}
        <br />
      </span>
      <b>Vdco:</b>
      <input type="number" v-model.number="parameters.Vdco" />
      <help :helpText="this.definitions.properties.Vdco.description" />
      <br />
      <span style="color:#F00;" v-if="'Vdco' in this.errors">
        {{ this.errors.Vdco }}
        <br />
      </span>
      <b>Pso:</b>
      <input type="number" v-model.number="parameters.Pso" />
      <help :helpText="this.definitions.properties.Pso.description" />
      <br />
      <span style="color:#F00;" v-if="'Pso' in this.errors">
        {{ this.errors.Pso }}
        <br />
      </span>
      <b>C0:</b>
      <input type="number" v-model.number="parameters.C0" />
      <help :helpText="this.definitions.properties.C0.description" />
      <br />
      <span style="color:#F00;" v-if="'C0' in this.errors">
        {{ this.errors.C0 }}
        <br />
      </span>
      <b>C1:</b>
      <input type="number" v-model.number="parameters.C1" />
      <help :helpText="this.definitions.properties.C1.description" />
      <br />
      <span style="color:#F00;" v-if="'C1' in this.errors">
        {{ this.errors.C1 }}
        <br />
      </span>
      <b>C2:</b>
      <input type="number" v-model.number="parameters.C2" />
      <help :helpText="this.definitions.properties.C2.description" />
      <br />
      <span style="color:#F00;" v-if="'C2' in this.errors">
        {{ this.errors.C2 }}
        <br />
      </span>
      <b>C3:</b>
      <input type="number" v-model.number="parameters.C3" />
      <help :helpText="this.definitions.properties.C3.description" />
      <br />
      <span style="color:#F00;" v-if="'C3' in this.errors">
        {{ this.errors.C3 }}
        <br />
      </span>
      <b>Pnt:</b>
      <input type="number" v-model.number="parameters.Pnt" />
      <help :helpText="this.definitions.properties.Pnt.description" />
      <br />
      <span style="color:#F00;" v-if="'Pnt' in this.errors">
        {{ this.errors.Pnt }}
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
      <b>eta_inv_nom:</b>
      <input type="number" v-model.number="parameters.eta_inv_nom" />
      <help :helpText="this.definitions.properties.eta_inv_nom.description" />
      <br />
      <span style="color:#F00;" v-if="'eta_inv_nom' in this.errors">
        {{ this.errors.eta_inv_nom }}
        <br />
      </span>
      <b>eta_inv_ref:</b>
      <input type="number" v-model.number="parameters.eta_inv_ref" />
      <help :helpText="this.definitions.properties.eta_inv_ref.description" />
      <br />
      <span style="color:#F00;" v-if="'eta_inv_ref' in this.errors">
        {{ this.errors.eta_inv_ref }}
        <br />
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import HelpPopup from "@/components/Help.vue";
import ArraysView from "@/components/Arrays.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

Vue.component("arrays-view", ArraysView);
Vue.component("help", HelpPopup);

@Component
export default class InverterParametersView extends ModelBase {
  // extend acceptable types for InverterParameters to include a PVWatts class
  @Prop() parameters!: SandiaInverterParameters | PVWattsInverterParameters;
  @Prop() model!: string;
  @Prop({ default: null }) selectedInverter!: string;

  data() {
    return {
      parameterSource: "User Supplied"
    };
  }

  loadInverter(event: any) {
    // TODO: load inverter from correct source based on selected model.
    console.log(event.target.value);
  }

  get parameterOptions() {
    // Return a list of parameter options based on currently selected model
    if (this.model == "pvsyst") {
      return ["PVSystInverter_0", "PVSystInverter_1"];
    } else if (this.model == "pvwatts") {
      return ["PVWattsInverter_0", "PVWattsInverter_1"];
    } else {
      return [];
    }
  }

  get apiComponentName() {
    let componentName: string;
    if (this.model == "pvsyst") {
      componentName = "SandiaInverterParameters";
    } else {
      componentName = "PVWattsInverterParameters";
    }
    return componentName;
  }

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    let params: Record<string, any>;
    if (this.model == "pvsyst") {
      params = newParams as SandiaInverterParameters;
    } else {
      params = newParams as PVWattsInverterParameters;
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
div.inverter-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
