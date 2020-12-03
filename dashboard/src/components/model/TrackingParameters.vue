<template>
  <div class="tracking-parameters">
    <div v-if="tracking == 'fixed'">
      <b>Tilt:</b>
      <input type="number" v-model.number="parameters.tilt" />
      <help :helpText="this.definitions.properties.tilt.description" />
      <br />
      <span style="color:#F00;" v-if="'tilt' in this.errors">
        {{ this.errors.tilt }}
        <br />
      </span>
      <b>Azimuth:</b>
      <input type="number" v-model.number="parameters.azimuth" />
      <help :helpText="this.definitions.properties.azimuth.description" />
      <br />
      <span style="color:#F00;" v-if="'azimuth' in this.errors">
        {{ this.errors.azimuth }}
        <br />
      </span>
    </div>
    <div v-if="tracking == 'singleAxis'">
      <b>Axis Tilt:</b>
      <input v-model.number="parameters.axis_tilt" />
      <help :helpText="this.definitions.properties.axis_tilt.description" />
      <br />
      <b>Axis Azimuth:</b>
      <input v-model.number="parameters.axis_azimuth" />
      <help :helpText="this.definitions.properties.axis_azimuth.description" />
      <br />
      <b>Ground Coverage Ratio:</b>
      <input v-model.number="parameters.gcr" />
      <help :helpText="this.definitions.properties.gcr.description" />
      <br />
    </div>
  </div>
</template>

<script lang="ts">
import ModelBase from "@/components/ModelBase.vue";
import HelpPopup from "@/components/Help.vue";

import { Component, Prop, Vue, Watch } from "vue-property-decorator";
import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";

Vue.component("help", HelpPopup);

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
