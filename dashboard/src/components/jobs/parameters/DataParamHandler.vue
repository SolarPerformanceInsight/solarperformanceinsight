<!--
  Component for handling the data parameters of a job. Takes the "jobTypeParams" as
  a Prop. This is an object containing a `compare` or `calculate` property and the
  associated job type string.

  Emits a `new-data-params` event that contains an object that should be merged into
  the root job parameters object.
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
      />
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
      if (this.jobTypeParams["calculate"] == "predicted performance") {
        return ["predicted"];
      } else {
        return ["expected"];
      }
    } else if (this.jobClass == "compare") {
      if (this.jobTypeParams["compare"] == "expected and actual performance") {
        // Single set of "data parameters" for both expected and actual performance
        return ["expected and actual"];
      } else if (
        this.jobTypeParams["compare"] == "predicted and actual performance"
      ) {
        return ["predicted", "actual"];
      } else {
        return ["predicted", "expected"];
      }
    } else {
      // Calculate PR, may need to be updated, required actual weather, actual performance
      // optionally provides "expected" modelled performance.
      return ["expected and actual"];
    }
  }
  emitParams(parameters?: Record<string, string>) {
    if (parameters) {
      this.$emit("new-data-params", parameters);
    } else {
      this.$emit("new-data-params", this.parameters);
    }
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
