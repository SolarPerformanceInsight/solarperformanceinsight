<!--
  Component for handling the data parameters of a job. 
  Props:
    jobTypeParams: an object containing the "calculate" or "compare" property and a
      string value as expected by the REST API.
      Example: 
        {
          calculate: "reference performance"
        }

  Emits a `new-data-params` event that contains an object that should be merged into
  the root job parameters object.
    Example event payloads:
      {
        weather_granularity: "system",
        irradiance_type: "standard",
        temperature_type: "cell"
      }
    Or:
      {
        reference_data_parameters: {
          data_available: "weather only",
          weather_granularity: "system",
          irradiance_type: "standard",
          temperature_type: "cell"
        },
        actual_data_parameters: {
          weather_granularity: "system",
          irradiance_type: "standard",
          temperature_type: "cell",
          performance_granularity: "system"
        }
      }

-->
<template>
  <div class="data-param-handler">
    <div class="grid-container my-1">
      <data-params
        v-for="dataType of requiredDataParams"
        :key="dataType"
        :dataType="dataType"
        :jobClass="jobClass"
        @new-data-params="setDataParams"
      >
        <template v-if="dataType == 'all_data' && jobClass == 'compare'">
          <span></span>
        </template>
      </data-params>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";

import DataParams from "@/components/jobs/parameters/DataParams.vue";

Vue.component("data-params", DataParams);

@Component
export default class DataParamHandler extends Vue {
  @Prop() jobTypeParams!: Record<string, string>;
  parameters!: Record<string, any>;
  data() {
    return {
      parameters: {}
    };
  }

  mounted() {
    this.emitParams();
  }

  setDataParams({
    type,
    parameters
  }: {
    type: string;
    parameters: Record<string, string>;
  }) {
    if (type == "data_parameters") {
      // Generic data_parameters type indicates that the data parameters should
      // be added to the root level job specification.
      this.parameters = parameters;
    } else {
      this.parameters[type] = parameters;
    }
    this.emitParams();
  }

  get isMonthly() {
    return (
      "compare" in this.jobTypeParams &&
      this.jobTypeParams["compare"].includes("monthly")
    );
  }

  get jobClass() {
    if ("compare" in this.jobTypeParams) {
      return "compare";
    } else if (
      this.jobTypeParams["calculate"] == "weather-adjusted performance ratio"
    ) {
      return "calculatepr";
    } else {
      return "calculate";
    }
  }
  get requiredDataParams() {
    if (this.isMonthly) {
      return [];
    }
    if (this.jobClass == "calculate") {
      if (this.jobTypeParams["calculate"] == "reference performance") {
        return ["reference"];
      } else {
        return ["modeled"];
      }
    } else if (this.jobClass == "compare") {
      if (this.jobTypeParams["compare"] == "modeled and actual performance") {
        // Single set of "data parameters" for both modeled and actual performance
        return ["all_data"];
      } else if (
        this.jobTypeParams["compare"] == "reference and actual performance"
      ) {
        return ["actual", "reference"];
      } else {
        return ["modeled", "reference"];
      }
    } else {
      // Calculate PR, may need to be updated, required actual weather, actual performance
      // optionally provides "modeled" modeled performance.
      return ["all_data"];
    }
  }
  emitParams() {
    this.$emit("new-data-params", this.parameters);
  }
  @Watch("jobTypeParams", { deep: true })
  resetParameters() {
    this.parameters = {};
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.grid-container {
  display: grid;
  grid-template-rows: auto auto;
}
.grid-container > div:nth-child(2) {
  padding-left: 1em;
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
