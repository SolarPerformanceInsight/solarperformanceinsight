<!--
  View for handling the "data_parameters" for a single type of data(Or the whole
  job if one set of data params is expected).

  Emits a new-data-params event with an object of the form: 
    {
      type: "predicted_data_params",
      params: {
        data_available(only for predicted in compare usecases),
        weather_granularity,
        irradiance_type,
        temperature_type,
        performance_granularity(when performance is included)
      }
    }

  Type will be set to `data_parameters`
-->
<template>
  <div class="data-parameters my-1">
    <h2 class="data-type">{{ dataType }}</h2>
    <div v-if="jobClass == 'compare' && this.dataType == 'predicted'">
      My predicted data includes:
      <br />
      <div class="ml-1 mt-1">
        <label>
          <input
            @change="emitParams"
            value="weather only"
            type="radio"
            v-model="data_available"
          />
          weather only.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="weather and AC performance"
            type="radio"
            v-model="data_available"
          />
          weather and AC performance.
        </label>
        <br />
        <label for="effective">
          <input
            @change="emitParams"
            value="weather, AC, and DC performance"
            type="radio"
            v-model="data_available"
          />
          weather, AC, and DC performance.
        </label>
        <br />
      </div>
    </div>
    <div v-if="data_available != 'weather only'" class="mt-1">
      I will provide performance data as:
      <br />
      <div class="ml-1 mt-1">
        <label>
          <input
            @change="emitParams"
            value="system"
            type="radio"
            v-model="performance_granularity"
          />
          one set for the entire system.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="inverter"
            type="radio"
            v-model="performance_granularity"
          />
          one set for each inverter and its associated arrays.
        </label>
        <br />
      </div>
    </div>
    <div class="my-1">
      My weather data file includes:
      <br />
      <div class="ml-1 mt-1">
        <label>
          <input
            @change="emitParams"
            value="standard"
            type="radio"
            v-model="irradiance_type"
          />
          global horizontal (GHI), direct normal (DNI), and diffuse horizontal
          (DHI) irradiance.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="poa"
            type="radio"
            v-model="irradiance_type"
          />
          global plane of array (POA global), direct plane of array (POA
          direct), and diffuse plane of array (POA diffuse) irradiance.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="effective"
            type="radio"
            v-model="irradiance_type"
          />
          effective irradiance.
        </label>
        <br />
      </div>
    </div>
    <div class="my-1">
      How should we determine cell temperature?
      <br />
      <div class="ml-1 mt-1">
        <label>
          <input
            @change="emitParams"
            value="air"
            type="radio"
            v-model="temperature_type"
          />
          Calculate cell temperature from irradiance, air temperature, and
          windspeed in my data.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="module"
            type="radio"
            v-model="temperature_type"
          />
          Calculate cell temperature from module temperature and irradiance in
          my data.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="cell"
            type="radio"
            v-model="temperature_type"
          />
          Cell temperature is included in my data.
        </label>
        <br />
      </div>
    </div>
    <div class="my-1">
      I will provide weather data as:
      <br />
      <div class="ml-1 mt-1">
        <label>
          <input
            @change="emitParams"
            value="system"
            type="radio"
            v-model="weather_granularity"
          />
          one set for the entire system.
        </label>
        <br />

        <label>
          <input
            @change="emitParams"
            value="inverter"
            type="radio"
            v-model="weather_granularity"
          />
          one set for each inverter and its associated arrays.
        </label>
        <br />
        <label>
          <input
            @change="emitParams"
            value="array"
            type="radio"
            v-model="weather_granularity"
          />
          one set for each array.
        </label>
        <br />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

@Component
export default class DataParams extends Vue {
  @Prop() dataType!: string;
  @Prop() jobClass!: string;
  data_available!: string;
  weather_granularity!: string;
  irradiance_type!: string;
  temperature_type!: string;
  performance_granularity!: string;

  data() {
    return {
      data_available: "weather only",
      irradiance_type: "standard",
      weather_granularity: "system",
      temperature_type: "air",
      performance_granularity: "system"
    };
  }
  created() {
    if (this.jobClass == "compare") {
      // Ensure the correct data availability is set for compare usecase
      // This field will not be included in the posted job JSON for
      // dataTypes other than predicted.
      if (this.dataType == "predicted") {
        this.data_available = "weather only";
      } else {
        this.data_available = "weather and AC performance";
      }
    }
  }
  mounted() {
    this.emitParams();
  }
  get parameters() {
    let type: string;
    const extraParameters: Record<string, string> = {};

    if (this.jobClass == "calculate" || this.jobClass == "calculatepr") {
      // calculate use case never includes performance data
      type = "data_parameters";
    } else {
      if (this.dataType == "predicted") {
        // Compare use cases using predicted data require the user to declare
        // if their data includes performance data, if it does they are expected to
        // provide the granularity of that data
        type = "predicted_data_parameters";
        extraParameters.data_available = this.data_available;
        if (this.data_available.includes("performance")) {
          extraParameters.performance_granularity = this.performance_granularity;
        }
      } else {
        if (this.dataType == "expected and actual") {
          type = "data_parameters";
        } else {
          type = `${this.dataType}_data_parameters`;
        }
        extraParameters.performance_granularity = this.performance_granularity;
      }
    }
    const params: Record<string, string | Record<string, string>> = {
      type: type,
      parameters: {
        irradiance_type: this.irradiance_type,
        weather_granularity: this.weather_granularity,
        temperature_type: this.temperature_type,
        ...extraParameters
      }
    };
    if (this.data_available.includes("performance")) {
      // @ts-expect-error
      params.parameters[
        "performance_granularity"
      ] = this.performance_granularity;
    }
    return params;
  }
  emitParams() {
    this.$emit("new-data-params", this.parameters);
  }
}
</script>
<style>
h2.data-type {
  text-transform: capitalize;
}
.data-parameters {
  grid-row: 1;
}
</style>
