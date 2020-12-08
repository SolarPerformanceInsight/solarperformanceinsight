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
      <model-field field-name="Paco" />
      <model-field field-name="Pdco" />
      <model-field field-name="Vdco" />
      <model-field field-name="Pso" />
      <model-field field-name="C0" />
      <model-field field-name="C1" />
      <model-field field-name="C2" />
      <model-field field-name="C3" />
      <model-field field-name="Pnt" />
    </div>
    <div v-if="model == 'pvwatts'">
      <model-field field-name="pdc0" />
      <model-field field-name="eta_inv_nom" />
      <model-field field-name="eta_inv_ref" />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import {
  SandiaInverterParameters,
  PVWattsInverterParameters
} from "@/types/InverterParameters";

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
