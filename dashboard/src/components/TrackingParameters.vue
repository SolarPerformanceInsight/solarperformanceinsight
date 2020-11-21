<template>
  <div class="tracking-parameters">
    <div v-if="tracking == 'fixed'">
      <b>Tilt: </b
      ><input type="number" v-model.number="parameters.tilt" /><br />
      <span style="color:#F00;" v-if="'tilt' in this.errors"
        >{{ this.errors.tilt }}<br
      /></span>
      <b>Azimuth: </b
      ><input type="number" v-model.number="parameters.azimuth" /><br />
      <span style="color:#F00;" v-if="'azimuth' in this.errors"
        >{{ this.errors.azimuth }}<br
      /></span>
    </div>
    <div v-if="tracking == 'singleAxis'">
      <b>Axis Tilt: </b><input v-model.number="parameters.axis_tilt" /><br />
      <b>Axis Azimuth: </b
      ><input v-model.number="parameters.axis_azimuth" /><br />
      <b>Ground Coverage Ratio: </b
      ><input v-model.number="parameters.gcr" /><br />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from "vue-property-decorator";
// Update with many classes of inverter parameters to check for type before
// choosing a display.
import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";

@Component
export default class TrackingParametersView extends Vue {
  @Prop() parameters!: FixedTrackingParameters | SingleAxisTrackingParameters;

  @Prop() tracking!: string;
  errors: Record<string, any> = {};

  @Watch("parameters", { deep: true })
  validate(newParams: Record<string, any>) {
    let params: Record<string, any>;
    let componentName: string;
    if (this.tracking == "fixed") {
      params = newParams as FixedTrackingParameters;
      componentName = "FixedTracking";
    } else {
      params = newParams as FixedTrackingParameters;
      componentName = "SingleAxisTracking";
    }

    this.$validator
      .validate(componentName, params)
      .then(this.setValidationResult);
  }
  setValidationResult(validity: boolean) {
    if (!validity) {
      const errors = this.$validator.getErrors();
      const currentErrors: Record<string, any> = {};
      errors.forEach(function(error: Record<string, any>) {
        const field = error.dataPath.split("/").pop();
        const message = error.message;
        currentErrors[field] = message;
      });
      this.errors = currentErrors;
    } else {
      this.errors = {};
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
div.tracking-parameters {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
