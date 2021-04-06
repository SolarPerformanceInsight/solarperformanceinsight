<template>
  <div class="module-parameters">
    <div v-if="model == 'pvsyst'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="gamma_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="mu_gamma"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="I_L_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="I_o_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_sh_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_sh_0"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_sh_exp"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_s"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="alpha_sc"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="EgRef"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="cells_in_series"
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
        field-name="gamma_pdc"
      />
    </div>
    <div v-if="model == 'sam'">
      <button class="show-browser" @click="showBrowser = true">
        Browse Module Database
      </button>
      <db-browser
        v-on="$listeners"
        @parameters-selected="showBrowser = false"
        @cancel-selection="showBrowser = false"
        v-if="showBrowser"
        browserType="module"
        :componentName="apiComponentName"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="alpha_sc"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="a_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="I_L_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="I_o_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_sh_ref"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="R_s"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="gamma_r"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="cells_in_series"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="Adjust"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="EgRef"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="dEgdT"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Watch } from "vue-property-decorator";

import ModelBase from "@/components/ModelBase.vue";

import {
  PVSystModuleParameters,
  PVWattsModuleParameters
} from "@/types/ModuleParameters";

@Component
export default class ModuleParametersView extends ModelBase {
  @Prop() parameters!: PVSystModuleParameters | PVWattsModuleParameters;
  @Prop({ default: "pvsyst" }) model!: string;
  showBrowser!: boolean;

  data() {
    return {
      showBrowser: false
    };
  }

  get apiComponentName() {
    if (this.model == "pvsyst") {
      return "PVsystModuleParameters";
    } else if (this.model == "sam") {
      return "CECModuleParameters";
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
