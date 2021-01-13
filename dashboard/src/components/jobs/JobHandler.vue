<!--
Component that handles basic job/workflows.
-->
<template>
  <div>
    <div v-if="this.system">
      <!-- Determine how to display the page header. We could be in one of two
           states here.
           - Job setup state: No job exists. Display generic "calculate",
               "compare" or "calculate pr" header"
           - Job exists: We have the type of job, display a more descriptive
               page header e.g. "Compare predicted and expected performance"
       -->
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
      <div class="errors" v-if="this.errorState">
        {{ this.errors }}
      </div>
      <!-- Sidebar displaying job steps -->
      <div v-else class="job-steps">
        <button
          class="jobtab"
          :class="{ active: step == 'setup' }"
          :disabled="job"
          @click="step = 'setup'"
        >
          Setup Calculation
          <br />
          <span class="step-status">{{ setupStatus }}</span>
        </button>
        <button v-if="dataSteps.length == 0" class="jobtab" disabled>
          Upload Data
          <br />
          <span class="step-status">{{ submitStatus }}</span>
        </button>
        <template v-if="dataSteps.length > 0">
          <button
            v-for="dataStep of dataSteps"
            :key="dataStep"
            class="jobtab"
            :class="{ active: step == dataStep }"
            :disabled="!job"
            @click="step = dataStep"
          >
            Upload {{ dataStep }}
            <br />
            <span class="step-status">{{ dataStepStatus[dataStep] }}</span>
          </button>
        </template>
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
            v-if="jobClass"
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
          <template v-if="step == 'original weather data'">
            <!-- Usecase 1A & 1B -->
            <csv-upload
              @data-uploaded="handleData"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :granularity="jobParameters.weather_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Original Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual weather data'">
            <csv-upload
              @data-uploaded="handleData"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :granularity="jobParameters.weather_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'predicted performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :granularity="jobParameters.job_type.performance_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Predicted Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'expected performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :granularity="jobParameters.job_type.performance_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Expected Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :jobId="jobId"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :granularity="jobParameters.job_type.performance_granularity"
              :irradiance_type="jobParameters.irradiance_type"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <!-- Performance upload step -->
        <keep-alive>
          <!-- Calculation submission step -->
          <template v-if="step == 'calculate'">
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
import JobParams from "@/components/jobs/parameters/JobParams.vue";

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
  errors!: Record<string, any>;

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
    // Callback for when setup completes. Pushes the new route of /jobs/<jobId>
    // which sets the jobId prop. Then, load the job from the api to get the
    // created data objects etc.
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
      if (this.jobStatus == "incomplete") {
        // Set current step to first job data type missing any data
        const dataStatus = this.dataStepStatus;
        let theStep = Object.keys(dataStatus)[0];
        for (const dataStep in dataStatus) {
          if (!(dataStatus[dataStep] == "Complete")) {
            theStep = dataStep;
            break;
          }
        }
        this.step = theStep;
      } else if (this.jobStatus == "error") {
        this.step = "error";
      } else if (this.jobStatus == "prepared") {
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
      return null;
    }
  }

  get dataSteps() {
    if (this.job) {
      return this.dataObjects
        .map((x: any) => {
          return x.definition.type;
        })
        .filter((v: string, i: number, self: Array<string>) => {
          return self.indexOf(v) === i;
        });
    }
    return [];
  }

  get dataStepStatus() {
    // Returns an object with keys of data_object types and values of status
    // strings for printing in the template above
    const dataStatus: Record<string, string> = {};
    for (const dataStep of this.dataSteps) {
      dataStatus[dataStep] = this.dataObjectStatus(dataStep);
    }
    return dataStatus;
  }

  filteredDataObjects(jobDataType = "any") {
    // Returns the data objects for the job with the type of `jobDataType`.
    // Special `any` value returns all data objects
    if (jobDataType != "any") {
      return this.dataObjects.filter(
        (x: any) => x.definition.type == jobDataType
      );
    }
    return this.dataObjects;
  }

  dataObjectsPresent(jobDataType = "any") {
    // Checks if all data objects with `type` of jobDataType are present
    return this.filteredDataObjects(jobDataType).every(
      (obj: any) => obj.definition.present
    );
  }

  dataObjectStatus(jobDataType = "any") {
    // Returns a status to display for the given job data type
    if (this.job) {
      if (this.dataObjectsPresent(jobDataType)) {
        return "Complete";
      } else {
        return "Needs data";
      }
    } else {
      return "Calculation Setup Required";
    }
  }

  get jobSteps() {
    let steps = ["setup"];
    if (this.job) {
      // Add in data steps
      steps = steps.concat(this.dataSteps);
      steps = steps.concat(["submit", "results"]);
    }
    return steps;
  }

  get setupStatus() {
    if (this.job) {
      return "Complete";
    } else {
      return "Requires setup";
    }
  }

  get submitStatus() {
    if (this.job) {
      if (this.job.status.status == "incomplete") {
        return "Data Upload Required";
      } else if (this.job.status.status == "prepared") {
        return "Ready For Calculation";
      } else {
        return "Submitted";
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
  handleData() {
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
  grid-template-columns: 250px 1fr;
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
