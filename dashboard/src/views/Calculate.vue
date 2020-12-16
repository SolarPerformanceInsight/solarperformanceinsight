<!-- View for workflows presented in usecases 1A and 1B
-->
<template>
  <div class="calculate-performance">
    Calculate Performance
    <template v-if="!jobSubmitted">
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
      <br />
      <button @click="submitJob">Get Started</button>
    </p>
    </template>
    <transition name="fade">
    <template v-if="jobSubmitted">
      <div v-if="workflow == 'predicted'">
        <br />
        <weather-upload><b>Step 1. Upload weather data</b></weather-upload>
        <button @click="submitCalculation">Submit Calculation</button>
        <li>Display Result</li>
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
    </template>
    </transition>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
@Component
export default class PredictPerformace extends Vue {
  workflow!: string;
  jobSubmitted!: boolean;
  data() {
    return {
      workflow: "predicted",
      jobSubmitted: false
    };
  }
  submitJob(){
    this.jobSubmitted = true;
  }
  submitCalculation(){
    console.log("Calculation submitted");
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
