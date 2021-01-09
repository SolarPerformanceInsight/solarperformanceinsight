<!--
Component that handles basic job/workflows.
-->
<template>
  <div>
    <div v-if="this.system">
      <h1 class="job-handler-title">
        <template v-if="jobClass == 'calculate'">
          Calculate
          <template v-if="job">
            {{ jobType.calculate }}
          </template>
          Performance
        </template>
        <template v-if="jobClass == 'compare'">
          Compare
          <template v-if="job">
            {{ jobType.compare }}
          </template>
          <template v-else>
          Performance
          </template>
        </template>
        <template v-if="jobClass == 'calculatepr'">
          Calculate Weather Adjusted Performance Ratio
        </template>
        For: {{ system.name }}
      </h1>
    </div>
    <div class="job-handler">
      <div v-if="this.errorState">
        {{ this.errors }}
      </div>
      <!-- Sidebar displaying job steps -->
      <div v-else class="job-steps">
        <button
          class="jobtab"
          :class="{ active: step == 'weather' }"
          :disabled="job"
          @click="step = 'setup'">
          Setup Calculation
          <br />
          <span class="step-status">{{ setupStatus }}</span>
        </button>
        <button
          class="jobtab"
          :class="{ active: step == 'weather' }"
          :disabled="!job"
          @click="step = 'weather'"
        >
          Upload Weather Data
          <br />
          <span class="step-status">{{ weatherStatus }}</span>
        </button>
        <button
          class="jobtab"
          :disabled="!job"
          :class="{ active: step == 'calculate' }"
          @click="step = 'calculate'"
        >
          Submit Calculation
          <br />
          <span class="step-status">{{ submitStatus }}</span>
        </button>
        <button
          class="jobtab"
          :disabled="!job"
          :class="{ active: step == 'results' }"
          @click="step = 'results'"
        >
          Results
          <br />
          <span class="step-status">{{ resultsStatus }}</span>
        </button>
      </div>
      <!-- Container to display active job step -->
      <div class="active-job-step">
        <template v-if="step == 'setup'">
          <job-params
            @job-created="loadCreatedJob"
            :systemId="systemId"
            :system="system"
            :jobClass="jobClass"
          ></job-params>
        </template>
        <!-- Keep alive keeps the rendered components in this components cached
             so that they don't get overwritten when different tabs are selected
          -->
        <keep-alive>
          <!-- Weather upload step -->
          <template v-if="step == 'weather'">
            <!-- Usecase 1A & 1B -->
            <weather-upload
              @weather-uploaded="handleWeather"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :weather_granularity="jobParameters.weather_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="weatherDataObjects"
            >
              <b>
                Upload
                <template
                  v-if="
                    jobParameters.job_type.calculate == 'predicted performance'
                  "
                >
                  Predicted
                </template>
                <template
                  v-if="
                    jobParameters.job_type.calculate == 'expected performance'
                  "
                >
                  Actual
                </template>
                Weather Data
              </b>
            </weather-upload>
          </template>

          <!-- Performance upload step -->
          <template v-else-if="step == 'performance'">
            <!-- Use cases 2A 2B 2C-->
            Not Implemented.
          </template>

          <!-- Calculation submission step -->
          <template v-else-if="step == 'calculate'">
            <button :disabled="jobStatus != 'prepared'">Compute</button>
            <span v-if="jobStatus != 'prepared'">
              Data must be uploaded before computation.
              <br />
            </span>
          </template>
          <!-- Error state -->
          <template v-else-if="jobStatus == 'error'">
            Something went wrong during report processing.
          </template>
        </keep-alive>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import JobParams from "@/components/jobs/JobParams.vue";

import { StoredSystem, System } from "@/types/System";
import { Inverter } from "@/types/Inverter";
import { PVArray } from "@/types/PVArray";
import * as Jobs from "@/api/jobs";

Vue.component("job-params", JobParams);
@Component
export default class JobHandler extends Vue {
  @Prop() typeOfJob!: string;
  @Prop() jobId!: string;
  @Prop() systemId!: string;
  loading!: boolean;
  job!: Record<string, any>;
  system!: System;
  step!: string;
  errorState!: boolean;
  errors: Record<string, any>;

  created() {
    if (this.jobId) {
      this.loadJob();
    } else {
      if (this.systemId) {
        this.loadSystem();
      }
    }
    this.setStep();
  }
  data() {
    return {
      job: null,
      loading: true,
      step: null,
      errorState: false,
      errors: {},
      system: null
    };
  }
  loadCreatedJob(jobId: string) {
    // Update route and trigger job loading.
    this.$router.push({
      name: "Job View",
      params: { jobId: jobId }
    });
    this.loadJob();
  }
  async loadJob() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.read(token, this.jobId);
    if (response.ok) {
      this.job = await response.json();
      this.system = this.job.definition.system_definition;
    } else {
      this.errorState = true;
      this.errors = {
        error: "Job not found."
      };
    }
    this.loading = false;
    this.setStep();
  }
  setStep() {
    if (this.job) {
      if (this.job.status.status == "incomplete") {
        this.step = "weather";
      } else if (this.job.status.status == "error") {
        this.step = "error";
      } else if (this.job.status.status == "prepared") {
        this.step = "calculate";
      } else {
        this.step = "results";
      }
    } else {
      this.step = "setup";
    }
  }
  get jobClass() {
    // Returns a generic job type of 'calculate', 'compare' or 'calculatepr'
    if (this.job) {
      // If we're past the creation step, infer job type from the job
      if ("performance_granularity" in this.jobType) {
        if ("compare" in this.jobType) {
          return "compare";
        } else {
          return "calculatepr";
        }
      } else {
        return "calculate";
      }
    } else {
      // Expect that the job type was passed as a prop
      return this.typeOfJob;
    }
  }
  get jobType() {
    if (this.job) {
      return this.jobParameters.job_type;
    }
    return null;
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
  get jobStatus() {
    if (this.job) {
      return this.job.status.status;
    } else {
      return "nonexistent";
    }
  }
  get setupStatus() {
    if (this.job) {
      return "Complete";
    } else {
      return "Requires setup";
    }
  }
  get weatherStatus() {
    if (this.job) {
      const a = 1;
      if (this.job.data_objects.every((obj: any) => obj.definition.present)) {
        return "Complete";
      } else {
        return "Needs data";
      }
    } else {
      return "Calculation Setup Required";
    }
  }
  get performanceStatus() {
    if (this.job) {
      return "Needs data";
    } else {
      return "Calculation Setup Required";
    }
  }
  get submitStatus() {
    if (this.job) {
      if (this.weatherStatus == "Complete") {
        return "Ready For Calculation";
      } else {
        return "Data Upload Required";
      }
    } else {
      return "Calculation Setup Required";
    }
  }
  get resultsStatus() {
    if (this.job) {
      if (this.job.status.status == "running") {
        return "Running";
      } else if (this.job.status.status == "complete") {
        return "Ready";
      } else if (this.job.status.status == "queued") {
        return "Queued";
      } else {
        return "Calculation Not Submitted";
      }
    } else {
      return "Calculation Setup Required";
    }
  }
  handleWeather() {
    // reload the job to get current state of data-objects
    this.loadJob();
  }
  async loadSystem() {
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(`/api/systems/${this.systemId}`, {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      })
    });
    if (response.ok) {
      const system = await response.json();
      this.system = new StoredSystem(system).definition;
    } else {
      this.errorState = true;
      this.errors = {
        error: "System not found."
      };
    }
  }
}
</script>
<style scoped>
.job-handler {
  display: grid;
  grid-template-columns: 200px 1fr;
  grid-template-areas: "sidebar main";
  gap: 0;
}
.job-steps {
  grid-area: sidebar;
}
.job-steps button {
  display: block;
  width: 100%;
  border: unset;
  height: 3em;
  text-align: left;
  flex-direction: column;
  border-bottom: 1px solid #bbb;
  border-right: 1px solid #bbb;
}
.job-steps button.active {
  background-color: #fff;
  border-right: unset;
}
.step-status {
  font-weight: bold;
}
.active-job-step {
  grid-area: main;
  padding-left: 1em;
}
h1 {
  font-size: 1.25em;
}
h1.job-handler-title {
  text-transform: capitalize;
}
</style>
