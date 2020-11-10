<template>
  <div class="tracking-parameters">
    <div v-if="tracking == 'fixed'">
      <b>Tilt: </b><input v-model="parameters.tilt" /><br />
      <b>Azimuth: </b><input v-model="parameters.tilt" /><br />
    </div>
    <div v-if="tracking == 'singleAxis'">
      <b>Axis Tilt: </b><input v-model="parameters.axis_tilt" /><br />
      <b>Axis Azimuth: </b><input v-model="parameters.axis_azimuth" /><br />
      <b>Ground Coverage Ratio: </b><input v-model="parameters.gcr" /><br />
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
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
