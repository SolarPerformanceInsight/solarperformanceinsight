<template>
  <div class="inverter-parameters">
    <template v-if="model == 'pvsyst'">
      <!-- Render an inverter browser for pvsyst model -->
      <button class="show-browser" @click="showBrowser = true">
        Browse Inverter Database
      </button>
      <db-browser
        v-on="$listeners"
        @parameters-selected="showBrowser = false"
        @cancel-selection="showBrowser = false"
        v-if="showBrowser"
        :componentName="apiComponentName"
      />
      <br />
    </template>
    <!-- If user selects something other than User Supplied, display the
         list of inverters from the db. This should probably be it's own
         component with some search functionality built in
     -->
    <div v-if="model == 'pvsyst'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Paco"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Pdco"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Vdco"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Pso"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="C0"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="C1"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="C2"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="C3"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Pnt"
      />
    </div>
    <div v-if="model == 'pvwatts'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="pdc0"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="eta_inv_nom"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="eta_inv_ref"
      />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Watch } from "vue-property-decorator";
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
  showBrowser = false;

  data() {
    return {
      parameterSource: "User Supplied",
      showBrowser: this.showBrowser
    };
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
