<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculate-params">
    <div class="my-1">
      <div class="my-1">
        I want to calculate the system output using...
        <br />
        <div class="ml-1 mt-1">
          <input
            @change="emitParams"
            id="predicted performance"
            value="predicted performance"
            type="radio"
            v-model="calculate"
          />
          <label for="predicted performance">
            weather data provided when the system was designed.
          </label>
          <br />
          <input
            @change="emitParams"
            id="expected performance"
            value="expected performance"
            type="radio"
            v-model="calculate"
          />
          <label for="expected performance">
            actual weather data during system operation.
          </label>
          <br />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class CalculateJobParams extends Vue {
  calculate!: string;

  data() {
    return {
      calculate: "predicted performance",
    };
  }
  mounted() {
    this.emitParams();
  }
  emitParams() {
    this.$emit("new-job-type-params", {calculate: this.calculate});
  }
}
</script>
