<!--
  View For handling common job parameters. Specific job parameters are
  inserted using the `jobParamComponent` fed to the <component> below.

-->
<template>
  <div class="calculated-data-parameters">
    <template>
        <div class="my-1">
            <div class="my-1">
              <div>
                My weather data file includes:
                <br />
                <div class="ml-1 mt-1">
                  <input
                    id="standard"
                    value="standard"
                    type="radio"
                    v-model="irradiance_type"
                  />
                  <label for="standard">
                    global horizontal (GHI), direct normal (DNI), and diffuse
                    horizontal (DHI) irradiance.
                  </label>
                  <br />
                  <input
                    id="poa"
                    value="poa"
                    type="radio"
                    v-model="irradiance_type"
                  />
                  <label for="poa">
                    global plane of array (POA global), direct plane of array
                    (POA direct), and diffuse plane of array (POA diffuse)
                    irradiance.
                  </label>
                  <br />
                  <input
                    id="effective"
                    value="effective"
                    type="radio"
                    v-model="irradiance_type"
                  />
                  <label for="effective">
                    effective irradiance.
                  </label>
                  <br />
                </div>
              </div>
              <div class="my-1">
                How should we determine cell temperature?
                <br />
                <div class="ml-1 mt-1">
                  <input
                    id="air"
                    value="air"
                    type="radio"
                    v-model="temperature_type"
                  />
                  <label for="air">
                    Calculate cell temperature from irradiance, air temperature,
                    and windspeed in my data.
                  </label>
                  <br />
                  <input
                    id="module"
                    value="module"
                    type="radio"
                    v-model="temperature_type"
                  />
                  <label for="module">
                    Calculate cell temperature from module temperature and
                    irradiance in my data.
                  </label>
                  <br />
                  <input
                    id="cell"
                    value="cell"
                    type="radio"
                    v-model="temperature_type"
                  />
                  <label for="cell">
                    Cell temperature is included in my data.
                  </label>
                  <br />
                </div>
              </div>
              <div class="my-1">
                I will provide weather data as:
                <br />
                <div class="ml-1 mt-1">
                  <input
                    id="system"
                    value="system"
                    type="radio"
                    v-model="weather_granularity"
                  />
                  <label for="system">
                    one set for the entire system.
                  </label>
                  <br />
                  <input
                    id="inverter"
                    value="inverter"
                    type="radio"
                    v-model="weather_granularity"
                  />
                  <label for="inverter">
                    one set for each inverter and its associated arrays.
                  </label>
                  <br />
                  <input
                    id="array"
                    value="array"
                    type="radio"
                    v-model="weather_granularity"
                  />
                  <label for="array">
                    one set for each array.
                  </label>
                  <br />
                </div>
              </div>
              <time-parameters
                :timeparams="timeParams"
                @new-timeparams="storeTimeParams"
              />
            </div>
            <div class="errors" v-if="this.apiErrors.length">
              <api-errors :errors="apiErrors" :fields="errorFields" />
            </div>
            <button class="mt-1" :disabled="!isValid" type="submit">
              Get Started
            </button>
            <span v-if="!isValid" class="warning-text">
              Start and End required.
            </span>
          </form>
        </div>
      </template>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { System } from "@/types/System";
import * as Jobs from "@/api/jobs";

import CalculateJobParams from "@/components/jobs/parameters/CalculateJobParams.vue";
import CompareJobParams from "@/components/jobs/parameters/CompareJobParams.vue";
import CalculatePRJobParams from "@/components/jobs/parameters/CalculatePRJobParams.vue";
import APIErrors from "@/components/ErrorRenderer.vue";

Vue.component("calculate-job-params", CalculateJobParams);
Vue.component("compare-job-params", CompareJobParams);
Vue.component("calculatepr-job-params", CalculatePRJobParams);
Vue.component("api-errors", APIErrors);

@Component
export default class JobParameters extends Vue {
  @Prop() systemId!: string;
  @Prop() system!: System;
  @Prop() jobClass!: string;

  errorFields = ["time_parameters"];

  jobTypeParams!: Record<string, string>;
  weather_granularity!: string;
  irradiance_type!: string;
  temperature_type!: string;
  jobSubmitted!: boolean;
  jobId!: string;

  apiErrors!: Array<Record<string, any>>;
  errorState!: boolean;
  timeParams!: Record<string, any>;
  jobSetupComponent!: string;

  data() {
    return {
      jobTypeParams: {},
      jobSubmitted: false,
      weather_granularity: "system",
      irradiance_type: "standard",
      apiErrors: [],
      errorState: false,
      temperature_type: "air",
      jobId: null,
      timeParams: {}
    };
  }
  storeTimeParams(timeParams: Record<string, any>) {
    this.timeParams = timeParams;
  }
  get jobSpec() {
    if (this.isMonthly) {
      return {
        system_id: this.systemId,
        ...this.jobTypeParams
      };
    } else {
      return {
        system_id: this.systemId,
        time_parameters: this.timeParams,
        weather_granularity: this.weather_granularity,
        irradiance_type: this.irradiance_type,
        temperature_type: this.temperature_type,
        ...this.jobTypeParams
      };
    }
  }
  get isValid() {
    // check that the start/end have been set, as they default to null
    return Boolean(
      this.isMonthly ||
        // @ts-expect-error
        (this.jobSpec.time_parameters.start && this.jobSpec.time_parameters.end)
    );
  }
  async postJob() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.create(token, this.jobSpec);
    if (response.ok) {
      const responseBody = await response.json();
      this.jobId = responseBody.object_id;
      this.jobSubmitted = true;
      this.$emit("job-created", this.jobId);
    } else {
      if (response.status == 422) {
        const responseBody = await response.json();
        this.apiErrors = responseBody.detail;
      } else {
        this.apiErrors = [
          {
            loc: ["error"],
            msg: `Failed to start job with error code ${response.status}`,
            type: "error"
          }
        ];
      }
      this.errorState = true;
    }
  }
  submitJob(e: any) {
    this.postJob();
    e.preventDefault();
  }
  get jobParamComponent() {
    return `${this.jobClass}-job-params`;
  }
  setJobTypeParams(newParams: Record<string, string>) {
    this.jobTypeParams = newParams;
  }
  get isMonthly() {
    return (
      "compare" in this.jobTypeParams &&
      this.jobTypeParams["compare"].includes("monthly")
    );
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.ml-1 {
  margin-left: 1em;
}
.my-1 {
  margin-top: 1em;
  margin-bottom: 1em;
}
.mt-1 {
  margin-top: 1em;
}
</style>
