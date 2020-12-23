<!--
Component that handles basic job/workflows.
-->
<template>
  <div class="job-handler">
    <template v-if="job">
      <template v-if="jobType == 'calculate'">
        <weather-upload
          :temperature_type="jobParameters.temperature_type"
          :system="job.definition.system_definition"
          :weather_granularity="jobParameters.weather_granularity"
          :irradiance_type="jobParameters.irradiance_type"
          :data_objects="weatherDataObjects"
        >
          <b>
            Upload
            <template
              v-if="jobParameters.job_type.calculate == 'predicted performance'"
            >
              Predicted
            </template>
            <template
              v-if="jobParameters.job_type.calculate == 'expected performance'"
            >
              Actual
            </template>
            Weather Data
          </b>
        </weather-upload>
      </template>
      <template v-if="jobType == 'compare'">
        Not Implemented.
      </template>
      <template v-if="jobType == 'calculate_pr'">
        Not Implemented.
      </template>
    </template>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import * as Jobs from "@/api/jobs";

@Component
export default class JobHandler extends Vue {
  @Prop() jobId!: string;
  loading!: boolean;
  job!: Record<string, any>;

  created() {
    this.loadJob();
  }
  data() {
    return {
      job: null,
      loading: true
    };
  }
  async loadJob() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.read(token, this.jobId);
    if (response.ok) {
      this.job = await response.json();
    } else {
      console.log("Failed to fetch job");
    }
    this.loading = false;
  }
  get jobType() {
    const jobTypeParams = this.jobParameters.job_type;
    if ("performance_granularity" in jobTypeParams) {
      if ("compare" in jobTypeParams) {
        return "compare";
      } else {
        return "calculate_pr";
      }
    } else {
      return "calculate";
    }
  }
  get weatherDataObjects() {
    // Get data objects pertaining to weather data
    return this.dataObjects.filter((x: any) =>
      x.definition.type.includes("weather")
    );
  }
  get performanceDataObjects() {
    // Get data objects pertaining to performance
    return this.dataObjects.filter((x: any) =>
      x.definition.type.includes("performance")
    );
  }
  get dataObjects() {
    return this.job.data_objects;
  }
  get jobParameters() {
    return this.job.definition.parameters;
  }
}
</script>
<style scoped></style>
