<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="compare-params">
    <div class="my-1">
      <div class="my-1">
        I want to compare:
        <br />
        <div class="ml-1 mt-1">
          <input
            @change="emitParams"
            id="predicted-and-actual-performance"
            value="predicted and actual performance"
            type="radio"
            v-model="compare"
          />
          <label for="predicted-and-actual-performance">
            predicted performance to actual performance.
          </label>
          <br />
          <input
            @change="emitParams"
            id="expected-and-actual-performance"
            value="expected and actual performance"
            type="radio"
            v-model="compare"
          />
          <label for="expected-and-actual-performance">
            expected performance to actual performance.
          </label>
          <br />
          <input
            @change="emitParams"
            id="predicted-and-expected-performance"
            value="predicted and expected performance"
            type="radio"
            v-model="compare"
            disabled="true"
          />
          <label class="greyed" for="predicted-and-expected-performance">
            predicted performance to expected performance.
          </label>
          <br />
        </div>
        <div v-if="containsPredicted">
          <p>What is the time resolution of your data?</p>
          <div class="ml-1 mt-1">
            <input
              type="radio"
              id="hourly-resolution"
              v-model="timeResolution"
              value="leHourly"
            />
            <label for="hourly-resolution">My data is hourly or better.</label>
            <br />
            <input
              disabled="true"
              type="radio"
              id="monthly-resolution"
              v-model="timeResolution"
              value="monthly"
            />
            <label class="greyed" for="monthly-resolution">
              My data is monthly.
            </label>
          </div>
        </div>
        <div v-if="validForGranularity" class="my-1">
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
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";

@Component
export default class CompareJobParams extends Vue {
  compare!: string;
  performance_granularity!: string;
  timeResolution!: string;

  data() {
    return {
      compare: "expected and actual performance",
      performance_granularity: "system",
      timeResolution: "leHourly"
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    let params = {
      compare: this.compare,
      performance_granularity: this.performance_granularity
    };
    if (this.containsPredicted && this.timeResolution == "monthly") {
      // @ts-expect-error
      params = {
        compare: `monthly ${this.compare}`
      };
    }
    this.$emit("new-job-type-params", params);
  }
  get containsPredicted() {
    return this.compare.includes("predicted");
  }
  get validForGranularity() {
    return !this.containsPredicted || this.timeResolution == "leHourly";
  }
  @Watch("timeResolution")
  resolutionChange() {
    this.emitParams();
  }
}
</script>

<style scoped>
.greyed {
  color: #9b9b9b;
}
</style>
