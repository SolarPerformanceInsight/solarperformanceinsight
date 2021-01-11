<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculatepr-params">
	<div class="my-1">
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
import { Component, Vue } from "vue-property-decorator";

@Component
export default class CalculatePRJobParams extends Vue {
  calculate!: string;
  performance_granularity!: string;

  data() {
    return {
      calculate: "weather-adjusted performance ratio",
      performance_granularity: "system"
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    this.$emit("new-job-type-params", {
      calculate: this.calculate,
      performance_granularity: this.performance_granularity
    });
  }
}
</script>
