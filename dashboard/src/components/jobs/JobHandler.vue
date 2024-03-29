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
               page header e.g. "Compare reference and modeled performance"
       -->
      <h1 class="job-handler-title">
        <template v-if="jobClass == 'calculate'">
          Calculate
          <template v-if="job">
            {{ jobParameters.calculate }}
          </template>
          <template v-else>
            Performance
          </template>
        </template>
        <template v-if="jobClass == 'compare'">
          Compare
          <template v-if="job">
            {{ jobParameters.compare }}
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
          <span class="step-status">{{ resultsStatus }}</span>
        </button>
        <template v-if="dataSteps.length > 0">
          <button
            v-for="dataStep of dataSteps"
            :key="dataStep"
            class="jobtab"
            :class="{ active: step == dataStep }"
            :disabled="
              !job ||
                ['calculate', 'queued', 'running', 'complete'].includes(
                  jobStatus
                )
            "
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
          <template v-if="step == 'reference weather data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Reference Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'reference monthly weather data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Reference Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual weather data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual monthly weather data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Weather Data</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'reference performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Reference Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'reference monthly performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Reference Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'modeled performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Modeled Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <keep-alive>
          <template v-if="step == 'actual monthly performance data'">
            <csv-upload
              @data-uploaded="handleData"
              :job="job"
              :temperature_type="jobParameters.temperature_type"
              :system="job.definition.system_definition"
              :data_objects="filteredDataObjects(step)"
            >
              <b>Upload Actual Performance</b>
            </csv-upload>
          </template>
        </keep-alive>
        <!-- Performance upload step -->
        <keep-alive>
          <template v-if="step == 'results'">
            <job-results
              @reload-job="fetchJob"
              @compute-job="computeJob"
              :jobType="jobClass"
              :job="job"
              :system="system"
            ></job-results>
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
import JobResults from "@/components/jobs/JobResults.vue";
import TimeseriesTable from "@/components/jobs/data/TimeseriesResultsTable.vue";
import { StoredSystem, System } from "@/types/System";
import * as Jobs from "@/api/jobs";

Vue.component("job-params", JobParams);
Vue.component("job-results", JobResults);
Vue.component("timeseries-table", TimeseriesTable);

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
  async fetchJob() {
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
  }
  async loadJob() {
    await this.fetchJob();
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
      } else if (this.jobStatus == "prepared") {
        this.step = "results";
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
      if ("compare" in this.jobParameters) {
        return "compare";
      } else {
        if (
          this.jobParameters.calculate == "weather-adjusted performance ratio"
        ) {
          return "calculatepr";
        } else {
          return "calculate";
        }
      }
    } else {
      // Expect that the job type was passed as a prop
      return this.typeOfJob;
    }
  }

  get dataObjects() {
    return this.job.data_objects;
  }

  get jobParameters() {
    const params = this.job.definition.parameters;
    return params;
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
      steps = steps.concat(["results"]);
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

  get resultsStatus() {
    if (this.job) {
      if (this.jobStatus == "running") {
        return "Running";
      } else if (this.jobStatus == "complete") {
        return "Ready";
      } else if (this.jobStatus == "queued") {
        return "Queued";
      } else if (this.jobStatus == "error") {
        return "An error occurred";
      } else {
        return "Data Required";
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
  async computeJob() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.compute(token, this.jobId);
    if (response.ok) {
      this.loadJob();
    } else {
      console.log("Could not compute");
    }
  }
}
</script>
<style scoped>
.job-handler {
  display: grid;
  grid-template-columns: 350px 1fr;
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
