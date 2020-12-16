<!-- View for workflows presented in use cases 2A, 2B and 2C.
-->
<template>
  <div class="compare-performance">
    Compare performance
    <p>
      I want to compare...<br />
      <input id="predicted-actual" value="predicted-actual" type="radio" v-model="workflow" />
      <label for="predicted-actual">
        predicted to actual performance.
      </label>
      <br />
      <input id="expected-actual" value="expected-actual" type="radio" v-model="workflow" />
      <label for="expected-actual">
        expected to actual performance.
      </label>
      <br />
      <input id="predicted-expected" value="predicted-expected" type="radio" v-model="workflow" />
      <label for="predicted-expected">
        predicted to expected performance.
      </label>
      <br />
    </p>
    <div v-if="workflow == 'predicted-actual'">
      Steps:
      <br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads predicted weather data</li>
        <li>user uploads predicted performance</li>
        <li>user uploads actual weather</li>
        <li>user uploads actual performance</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
    </div>
    <div v-if="workflow == 'predicted-expected'">
      Steps:
      <br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads predicted weather data</li>
        <li>user uploads predicted performance</li>
        <li>user uploads actual weather</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
    </div>
    <div v-if="workflow == 'expected-actual'">
      Steps:
      <br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads actual weather</li>
        <li>user uploads actual performance</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class ComparePerformance extends Vue {
  workflow!: string;
  data() {
    return {
      workflow: "predicted-actual"
    };
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
