<!--
Component that handles basic job/workflows.
-->
<template>
  <div class="job-handler">
    <template v-if="jobType == 'calculate'">
      <weather-upload
        :temperature_type="jobParameters.temperature_type"
        :system="job.definition.system"
        :weather_granularity="jobParameters.weather_granularity"
        :irradiance_type="jobParameters.irradiance_type"
      >
       <b>Step 1: Upload
       <template v-if="jobParameters.job_type.calculate == 'predicted_performance'">
       Predicted
       </template>
       <template v-if="jobParameters.job_type.calculate == 'expected_performance'">
       Actual
       </template>
       Weather Data</b>
      </weather-upload>
    </template>
    <template v-if="jobType == 'compare'">
      Not Implemented.
    </template>
    <template v-if="jobType == 'calculate_pr'">
      Not Implemented.
    </template>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component
export default class JobHandler extends Vue {
  @Prop() jobId!: string;
  @Prop() job!: Record<string, any>; // TODO: convert to data after loading job

  loadJob() {
    // TODO: load job from the api.
    return;
  }
  get jobType() {
    // TODO: examine job object and return appropriate type.
    return "calculate";
  }
  get jobParameters() {
    return this.job.definition.parameters;
  }
}
</script>
<style scoped>
</style>
