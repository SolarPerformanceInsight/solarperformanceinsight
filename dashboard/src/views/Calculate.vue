<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculate-performance">
    <div v-if="errorState">
      {{ apiErrors }}
    </div>
    <template v-if="!systemLoading && !errorState">
      Calculate Performance For System
      <b>{{ system.definition.name }}</b>
      <br />
      <template v-if="!jobSubmitted">
        <div class="my-1">
          <div class="my-1">
            I want to calculate the system output using...
            <br />
            <div class="ml-1 mt-1">
              <input
                id="predicted_performance"
                value="predicted_performance"
                type="radio"
                v-model="calculate"
              />
              <label for="predicted">
                weather data provided when the system was designed.
              </label>
              <br />
              <input
                id="expected_performance"
                value="expected_performance"
                type="radio"
                v-model="calculate"
              />
              <label for="expected_performance">
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
              <input id="poa" value="poa" type="radio" v-model="irradiance_type" />
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
              <input id="air" value="air" type="radio" v-model="temperature_type" />
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
          <button class="mt-1" @click="submitJob">Get Started</button>
        </div>
      </template>
      <transition name="fade">
        <template v-if="jobSubmitted">
          <job-handler :job="mockStoredJob"/>
        </template>
      </transition>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";
import { StoredSystem } from "@/types/System";

@Component
export default class PredictPerformace extends Vue {
  @Prop() systemId!: string;
  system!: StoredSystem;
  calculate!: string;
  weather_granularity!: string;
  irradiance_type!: string;
  temperature_type!: string;
  jobSubmitted!: boolean;

  // TODO: refactor common api/404 code
  apiErrors!: Record<string, any>;
  errorState!: boolean;
  systemLoading!: boolean;

  created() {
    this.systemLoading = true;
    if (this.systemId !== undefined) {
      this.loadSystem();
    } else {
      this.apiErrors = { 404: "System not found." };
      this.errorState = true;
      this.systemLoading = false;
    }
  }
  data() {
    return {
      calculate: "predicted_performance",
      jobSubmitted: false,
      weather_granularity: "system",
      irradiance_type: "standard",
      system: this.system,
      systemLoading: this.systemLoading,
      apiErrors: {},
      errorState: false,
      temperature_type: "cell"
    };
  }
  get jobSpec() {
    return {
      system_id: this.system.object_id,
      job_type: {
        calculate: this.calculate
      },
      weather_granularity: this.weather_granularity,
      irradiance_type: this.irradiance_type,
      temperature_type: this.temperature_type
    };
  }
  get mockStoredJob() {
    // Temporary method to mock/pass stored job result to child component.
    return {
      definition: {
        system: this.system.definition,
        parameters: this.jobSpec
      },
      status: "incomplete",
      data_objects: []
    }
  }
  async submitJob() {
    // TODO: post jobSpec
    // const token = this.$auth.getTokenSilently();
    // const response = await fetch('/jobs/', {
    //   method: "post,
    //   body: JSON.stringify(this.jobSpec)
    //   headers: new Headers({
    //     Authorization: `Bearer ${token}`
    //   })
    // });
    // if (response.ok) { this.jobId = response.json().object_id };
    this.jobSubmitted = true;
  }
  submitCalculation() {
    // TODO: Check job status, if ready, submit.
    console.log("Calculation submitted");
  }
  async loadSystem() {
    this.systemLoading = true;
    const token = await this.$auth.getTokenSilently();
    const response = await fetch(`/api/systems/${this.systemId}`, {
      headers: new Headers({
        Authorization: `Bearer ${token}`
      })
    });
    if (response.ok) {
      const system = await response.json();
      this.system = new StoredSystem(system);
      this.systemLoading = false;
    } else {
      this.errorState = true;
      this.apiErrors = {
        error: "System not found."
      };
      this.systemLoading = false;
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
