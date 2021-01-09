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
          />
          <label for="predicted-and-expected-performance">
            predicted performance to expected performance.
          </label>
          <br />
        </div>
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
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class CompareJobParams extends Vue {
  compare!: string;
  performance_granularity!: string;

  data() {
    return {
      compare: "predicted and actual performance",
	  performance_granularity: "system"
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    this.$emit("new-job-type-params", {
	  compare: this.compare,
	  performance_granularity: this.performance_granularity
	});
  }
}
</script>
