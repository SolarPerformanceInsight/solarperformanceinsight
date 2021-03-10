<!--
  View for handling the PredictedDataParams object.

  Emits a new-data-params event with an object of the form: 
    {
      type: "predicted_data_params",
      params: {
        ...parameters
      }
    }
-->
<template>
  <div class="expected-actual-data-parameters my-1">
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
          global horizontal (GHI), direct normal (DNI), and diffuse horizontal
          (DHI) irradiance.
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
        <input id="air" value="air" type="radio" v-model="temperature_type" />
        <label for="air">
          Calculate cell temperature from irradiance, air temperature, and
          windspeed in my data.
        </label>
        <br />
        <input
          id="module"
          value="module"
          type="radio"
          v-model="temperature_type"
        />
        <label for="module">
          Calculate cell temperature from module temperature and irradiance in
          my data.
        </label>
        <br />
        <input id="cell" value="cell" type="radio" v-model="temperature_type" />
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
    <div>
      I will provide performance data as:
      <br />
      <div class="ml-1 mt-1">
        <input
          id="system"
          value="system"
          type="radio"
          v-model="performance_granularity"
        />
        <label for="system">
          one set for the entire system.
        </label>
        <br />
        <input
          id="inverter"
          value="inverter"
          type="radio"
          v-model="performance_granularity"
        />
        <label for="inverter">
          one set for each inverter and its associated arrays.
        </label>
        <br />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component
export default class ExpectedActualDataParams extends Vue {
  @Prop() type?: string;
  weather_granularity!: string;
  irradiance_type!: string;
  temperature_type!: string;
  performance_granularity!: string;

  data() {
    return {
      irradiance_type: "standard",
      weather_granularity: "system",
      temperature_type: "air",
      performance_granularity: "system"
    };
  }
  mounted() {
    this.emitParams();
  }
  get parameters() {
    let type = this.type;
    if (!type) {
      // special type used for both expected and actual parameters for usecase 2C: Compare expected and actual performance
      type = "expected and actual parameters";
    }
    return {
      type: type,
      parameters: {
        irradiance_type: this.irradiance_type,
        temperature_type: this.temperature_type,
        weather_granularity: this.weather_granularity
      }
    };
  }
  emitParams() {
    this.$emit("new-data-params", this.parameters);
  }
}
</script>
<style>
.expected-actual-data-parameters {
  grid-row: 1;
}
</style>
