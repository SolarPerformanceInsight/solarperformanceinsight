<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="predict-performance">
    <p>I want to:
    <select v-model="workflow">
      <option value="predicted">calculate predicted performance.</option>
      <option value="expected">calculate expected performance.</option>
    </select>
    </p>
    <div v-if="workflow=='predicted'">
      Steps:<br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads predicted weather data</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
    </div>
    <div v-if="workflow=='expected'">
      Steps:<br />
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
      workflow: "predicted",
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
