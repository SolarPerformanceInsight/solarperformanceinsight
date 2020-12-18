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
                id="predicted"
                value="predicted"
                type="radio"
                v-model="workflow"
              />
              <label for="predicted">
                weather data provided when the system was designed.
              </label>
              <br />
              <input
                id="expected"
                value="expected"
                type="radio"
                v-model="workflow"
              />
              <label for="expected">
                actual weather data during system operation.
              </label>
              <br />
            </div>
          </div>
          <div class="my-1">
            My data files includes:
            <br />
            <div class="ml-1 mt-1">
              <input
                id="standard"
                value="standard"
                type="radio"
                v-model="weather_type"
              />
              <label for="standard">
                global horizontal (GHI), direct normal (DNI), and diffuse
                horizontal (DHI) irradiance.
              </label>
              <br />
              <input id="poa" value="poa" type="radio" v-model="weather_type" />
              <label for="poa">
                global plane of array (POA global), direct plane of array(POA
                direct), and diffuse plane of array(POA diffuse) irradiance.
              </label>
              <br />
              <input
                id="effective"
                value="effective"
                type="radio"
                v-model="weather_type"
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
                v-model="temperature"
              />
              <label for="cell">
                Cell temperature is included in my data.
              </label>
              <br />
              <input
                id="module"
                value="module"
                type="radio"
                v-model="temperature"
              />
              <label for="module">
                Calculate cell temperature from module temperature and irradiance in my data.
              </label>
              <br />
              <input id="air" value="air" type="radio" v-model="temperature" />
              <label for="air">
                Calculate cell temperature from irradiance, air temperature, and
                windspeed in my data.
              </label>
              <br />
            </div>
          </div>
          <div class="my-1">
            I have data for:
            <br />
            <div class="ml-1 mt-1">
              <input
                id="system"
                value="system"
                type="radio"
                v-model="weather_granularity"
              />
              <label for="system">
                the entire system.
              </label>
              <br />
              <input
                id="inverter"
                value="inverter"
                type="radio"
                v-model="weather_granularity"
              />
              <label for="inverter">
                each inverter.
              </label>
              <br />
              <input
                id="array"
                value="array"
                type="radio"
                v-model="weather_granularity"
              />
              <label for="array">
                each array.
              </label>
              <br />
            </div>
          </div>
          <button class="mt-1" @click="submitJob">Get Started</button>
        </div>
      </template>
      <transition name="fade">
        <template v-if="jobSubmitted">
          <div v-if="workflow == 'predicted'">
            <br />
            <weather-upload
              :temperature="temperature"
              :system="system"
              :weather_granularity="weather_granularity"
              :weather_type="weather_type"
            >
              <b>Step 1. Upload weather data</b>
            </weather-upload>
            <button @click="submitCalculation">Submit Calculation</button>
            <li>Display Result</li>
          </div>
          <div v-if="workflow == 'expected'">
            Steps:
            <br />
            <ol>
              <li>register job(user clicks "get started")</li>
              <li>user uploads actual weather data</li>
              <li>submit calculation</li>
              <li>Display Result</li>
            </ol>
          </div>
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
  workflow!: string;
  weather_granularity!: string;
  weather_type!: string;
  temperature!: string;
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
      workflow: "predicted",
      jobSubmitted: false,
      weather_granularity: "system",
      weather_type: "standard",
      system: this.system,
      systemLoading: this.systemLoading,
      apiErrors: {},
      errorState: false,
      temperature: "cell"
    };
  }
  submitJob() {
    this.jobSubmitted = true;
  }
  submitCalculation() {
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
