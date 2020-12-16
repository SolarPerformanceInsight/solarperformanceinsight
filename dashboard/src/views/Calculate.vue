<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculate-performance">
    Calculate Performance
    <p>
      I want to calculate the system output using...
      <br />
      <input id="predicted" value="predicted" type="radio" v-model="workflow" />
      <label for="predicted">
        weather data provided when the system was designed.
      </label>
      <br />
      <input id="expected" value="expected" type="radio" v-model="workflow" />
      <label for="expected">
        actual weather data during system operation.
      </label>
    </p>
    <div v-if="workflow == 'predicted'">
      Steps:
      <br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads predicted weather data</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
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
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
@Component
export default class PredictPerformace extends Vue {
  workflow!: string;
  data() {
    return {
      workflow: "predicted"
    };
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
