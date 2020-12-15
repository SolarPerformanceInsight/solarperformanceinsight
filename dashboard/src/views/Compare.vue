<!-- View for workflows presented in use cases 2A, 2B and 2C.
-->
<template>
  <div class="compare-performance">
    Compare performance
    <p>I want to:
    <select v-model="workflow">
      <option value="predicted-actual">compare predicted to actual performance.</option>
      <option value="expected-actual">compare expected to actual performance.</option>
      <option value="predicted-expected">compre predicted to expected performance.</option>
    </select>
    </p>
    <div v-if="workflow=='predicted-actual'">
      Steps:<br />
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
    <div v-if="workflow=='predicted-expected'">
      Steps:<br />
      <ol>
        <li>register job(user clicks "get started")</li>
        <li>user uploads predicted weather data</li>
        <li>user uploads predicted performance</li>
        <li>user uploads actual weather</li>
        <li>submit calculation</li>
        <li>Display Result</li>
      </ol>
    </div>
    <div v-if="workflow=='expected-actual'">
      Steps:<br />
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
