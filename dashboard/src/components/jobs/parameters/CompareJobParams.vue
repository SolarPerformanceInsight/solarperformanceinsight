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
            id="reference-and-actual-performance"
            value="reference and actual performance"
            type="radio"
            v-model="compare"
          />
          <label for="reference-and-actual-performance">
            reference performance to actual performance.
          </label>
          <br />
          <input
            @change="emitParams"
            id="modeled-and-actual-performance"
            value="modeled and actual performance"
            type="radio"
            v-model="compare"
          />
          <label for="modeled-and-actual-performance">
            modeled performance to actual performance.
          </label>
          <br />
          <input
            @change="emitParams"
            id="reference-and-modeled-performance"
            value="reference and modeled performance"
            type="radio"
            v-model="compare"
            disabled="true"
          />
          <label class="greyed" for="reference-and-modeled-performance">
            reference performance to modeled performance.
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
            <label for="hourly-resolution">
              My data is hourly or better.
            </label>
            <br />
            <input
              type="radio"
              id="monthly-resolution"
              v-model="timeResolution"
              value="monthly"
            />
            <label for="monthly-resolution">
              My data is monthly.
            </label>
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
  timeResolution!: string;

  data() {
    return {
      compare: "reference and actual performance",
      timeResolution: "leHourly"
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    let params = {
      compare: this.compare
    };
    if (this.containsPredicted && this.timeResolution == "monthly") {
      params = {
        compare: `monthly ${this.compare}`
      };
    }
    this.$emit("new-job-type-params", params);
  }
  get containsPredicted() {
    return this.compare.includes("reference");
  }
  @Watch("compare")
  ensureValidTimeResolution() {
    // Ensure that if we're not working with
    if (!this.containsPredicted) {
      this.timeResolution = "leHourly";
    }
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
