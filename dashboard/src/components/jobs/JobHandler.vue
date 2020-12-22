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
        :data_objects="dataObjects"
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
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";

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
  get dataObjects() {
    // TODO: use data objects from api object
    const params = this.jobParameters;
    let dataType: string;
    if (params.job_type.calculate == "predicted_performance") {
      dataType = "original_weather";
    } else {
      dataType = "actual_weather";
    }
    let dataObjects: Array<Record<string, any>> = [];
    if (params.weather_granularity == "system") {
      dataObjects = [{
        schema_path: "/",
        type: dataType,
        filename: "0.arrow",
        data_format: "application/vnd.apache.arrow.file",
        present: "false"
      }];
    } else if (params.weather_granularity == "inverter") {
      this.job.definition.system.inverters.forEach(function(inverter: Inverter, i: number) {
        dataObjects.push({
          schema_path: `/inverters/${i}`,
          type: dataType,
          filename: "0.arrow",
          data_format: "application/vnd.apache.arrow.file",
          present: "false"
        });
      });
    } else {
      this.job.definition.system.inverters.forEach(function(inverter: Inverter, i: number) {
        inverter.arrays.forEach(function(pvarray: PVArray, j: number) {
          dataObjects.push({
            schema_path: `/inverters/${i}/arrays/${j}`,
            type: dataType,
            filename: "0.arrow",
            data_format: "application/vnd.apache.arrow.file",
            present: "false"
          });
        });
      });
    }
    return dataObjects;
  }
  get jobParameters() {
    return this.job.definition.parameters;
  }
}
</script>
<style scoped>
</style>
