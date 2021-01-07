<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculate-performance">
    <div v-if="errorState">
      {{ apiErrors }}
    </div>
    <template v-if="!errorState">
      Calculate Performance For System
      <b>{{ system.name }}</b>
      <br />
      <template v-if="!jobSubmitted">
        <div class="my-1">
          <div class="my-1">
            I want to calculate the system output using...
            <br />
            <div class="ml-1 mt-1">
              <input
                id="predicted performance"
                value="predicted performance"
                type="radio"
                v-model="calculate"
              />
              <label for="predicted performance">
                weather data provided when the system was designed.
              </label>
              <br />
              <input
                id="expected performance"
                value="expected performance"
                type="radio"
                v-model="calculate"
              />
              <label for="expected performance">
                actual weather data during system operation.
              </label>
              <br />
            </div>
          </div>
          <div class="my-1">
            My data file includes:
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
                global plane of array (POA global), direct plane of array (POA
                direct), and diffuse plane of array (POA diffuse) irradiance.
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
                id="cell"
                value="cell"
                type="radio"
                v-model="temperature_type"
              />
              <label for="cell">
                Cell temperature is included in my data.
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
                id="air"
                value="air"
                type="radio"
                v-model="temperature_type"
              />
              <label for="air">
                Calculate cell temperature from irradiance, air temperature, and
                windspeed in my data.
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
          <time-parameters @new-timeparams="storeTimeParams" />
          <button class="mt-1" @click="submitJob">Get Started</button>
        </div>
      </template>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { System } from "@/types/System";
import * as Jobs from "@/api/jobs";
@Component
export default class CalculateJobCreator extends Vue {
  @Prop() systemId!: string;
  @Prop() system!: System;
  calculate!: string;
  weather_granularity!: string;
  irradiance_type!: string;
  temperature_type!: string;
  jobSubmitted!: boolean;
  jobId!: string;

  // TODO: refactor common api/404 code
  apiErrors!: Record<string, any>;
  errorState!: boolean;
  timeParams!: Record<string, any>;

  data() {
    return {
      calculate: "predicted performance",
      jobSubmitted: false,
      weather_granularity: "system",
      irradiance_type: "standard",
      apiErrors: {},
      errorState: false,
      temperature_type: "cell",
      jobId: null
    };
  }
  storeTimeParams(timeParams: Record<string, any>) {
    this.timeParams = timeParams;
  }
  get jobSpec() {
    return {
      system_id: this.systemId,
      job_type: {
        calculate: this.calculate
      },
      time_parameters: this.timeParams,
      weather_granularity: this.weather_granularity,
      irradiance_type: this.irradiance_type,
      temperature_type: this.temperature_type
    };
  }
  async submitJob() {
    const token = await this.$auth.getTokenSilently();
    const response = await Jobs.create(token, this.jobSpec);
    if (response.ok) {
      const responseBody = await response.json();
      this.jobId = responseBody.object_id;
      this.jobSubmitted = true;
      this.$emit("job-created", this.jobId);
    } else {
      this.errorState = true;
      if (response.status == 422) {
        const responseBody = await response.json();
        this.apiErrors = responseBody.detail;
      } else {
        this.apiErrors = {
          error: `Failed to start job with error code ${response.status}`
        };
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
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
