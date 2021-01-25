<template>
  <div class="tracking-parameters">
    <div v-if="tracking == 'fixed'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="tilt"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="azimuth"
      />
    </div>
    <div v-if="tracking == 'singleAxis'">
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="axis_tilt"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="axis_azimuth"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="gcr"
      />
      <model-field
        :parameters="parameters"
        :errors="errors"
        :definitions="definitions"
        field-name="backtracking"
      />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";

import { Component, Prop, Watch } from "vue-property-decorator";
import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";

@Component
export default class TrackingParametersView extends ModelBase {
  @Prop() parameters!: FixedTrackingParameters | SingleAxisTrackingParameters;

  @Prop() tracking!: string;
  errors: Record<string, any> = {};

  get apiComponentName() {
    //Select the correct key from the api spec based on current tracking type
    let componentName: string;
    if (this.tracking == "fixed") {
      componentName = "FixedTracking";
    } else {
      componentName = "SingleAxisTracking";
    }
    return componentName;
  }

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    let params: Record<string, any>;
    if (this.tracking == "fixed") {
      params = newParams as FixedTrackingParameters;
    } else {
      params = newParams as FixedTrackingParameters;
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
div.tracking-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
