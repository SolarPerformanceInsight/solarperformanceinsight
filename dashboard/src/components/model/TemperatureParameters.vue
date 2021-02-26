<template>
  <div class="temperature-parameters">
    <label for="mountDefaults"><b>Defaults:</b></label>
    <select @change="mounting" name="mountDefaults">
      <option value="" selected>Manually Set Parameters</option>
      <option v-for="k in mountOptions" :key="k" :name="k" :value="k">
        {{ k }}
      </option>
    </select>
    <div v-if="model == 'pvsyst' || model == 'sam'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="u_c"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="u_v"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="alpha_absorption"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="eta_m"
      />
    </div>
    <div v-if="model == 'pvwatts'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="a"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="b"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="deltaT"
      />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import DefaultParams from "@/constants/temp_params.json";
import { Component, Prop, Watch } from "vue-property-decorator";

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
  defaultMap: Record<
    string,
    Record<
      string,
      Partial<PVSystTemperatureParameters> | SAPMTemperatureParameters
    >
  > = DefaultParams;

  get apiComponentName() {
    let componentName: string;
    if (this.model == "pvsyst" || this.model == "sam") {
      componentName = "PVsystTemperatureParameters";
    } else {
      componentName = "SAPMTemperatureParameters";
    }
    return componentName;
  }

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    this.$validator
      .validate(this.apiComponentName, newParams)
      .then(this.setValidationResult);
  }

  get mountOptions() {
    let params: Array<string>;
    if (this.model == "pvsyst" || this.model == "sam") {
      params = Object.keys(this.defaultMap.pvsyst);
    } else {
      params = Object.keys(this.defaultMap.sapm);
    }
    return params;
  }
  mounting(event: any) {
    const mountOpt = event.target.value;
    let newvals;
    // Empty string indicates custom input
    if (mountOpt) {
      if (this.model == "pvsyst" || this.model == "sam") {
        newvals = this.defaultMap.pvsyst[mountOpt];
      } else {
        newvals = this.defaultMap.sapm[mountOpt];
      }
      this.parameters = Object.assign(this.parameters, newvals);
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
div.temperature-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
