<!--
  View For handling common job parameters. Specific job parameters are
  inserted using the `jobParamComponent` fed to the <component> below.

-->
<template>
  <div class="calculate-performance">
    <template>
      <template v-if="!jobSubmitted">
        <div class="my-1">
          <form id="job-parameters" @submit="submitJob">
            <!-- For selecting between diferent usecase variants e.g. CompareJobParams
                 Allows user to select betweel predicted-actual, expected-actual, and
                 predicted expected.    
            -->
            <component
              v-bind:is="jobParamComponent"
              @new-job-type-params="setJobTypeParams"
            />

            <!-- Prompts user about special requirements for monthly data -->
            <div v-if="isMonthly">
              <p>
                When comparing monthly data users are expected to provide
                monthly totals of energy and POA insolation and monthly average
                daytime cell temperature. Monthly data should be provided as one
                set for the entire system and include all 12 months.
              </p>
            </div>

            <div v-if="!isMonthly" class="my-1">
              <data-param-handler
                v-if="Object.keys(jobTypeParams).length"
                :jobTypeParams="jobTypeParams"
                @new-data-params="setDataParams"
              />
              <time-parameters
                :timeparams="timeParams"
                @new-timeparams="storeTimeParams"
              >
                <template
                  v-if="
                    jobTypeParams.compare &&
                      jobTypeParams.compare.includes('predicted')
                  "
                >
                  Predicted data may be provided for a different year from the
                  time index described below. An attempt will be made to shift
                  predicted data by full years to match the index. The timestep
                  and the month, day, and time of the start and end of the
                  predicted data must match the index. Any extra timestamps in
                  the predicted data will be ignored, for instance when February
                  29th exists in the predicted data but not in the index. When
                  shifting predicted data from a non-leap year to a leap year,
                  February 29 will be dropped from the analysis.
                </template>
              </time-parameters>
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
import DataParamHandler from "@/components/jobs/parameters/DataParamHandler.vue";

import APIErrors from "@/components/ErrorRenderer.vue";

Vue.component("calculate-job-params", CalculateJobParams);
Vue.component("compare-job-params", CompareJobParams);
Vue.component("calculatepr-job-params", CalculatePRJobParams);
Vue.component("api-errors", APIErrors);
Vue.component("data-param-handler", DataParamHandler);

@Component
export default class JobParameters extends Vue {
  @Prop() systemId!: string;
  @Prop() system!: System;
  @Prop() jobClass!: string;

  errorFields = ["time_parameters"];

  jobTypeParams!: Record<string, string>;
  dataParams!: Record<string, any>;
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
      apiErrors: [],
      errorState: false,
      jobId: null,
      timeParams: {},
      dataParams: {}
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
        ...this.jobTypeParams,
        ...this.dataParams
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

  setDataParams(parameters: Record<string, any>) {
    this.dataParams = parameters;
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
.grid-container {
  display: grid;
  grid-template-rows: auto auto;
}
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
