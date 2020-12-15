<!--View for workflow presented in usecase 2D
-->
<template>
  <div class="calculate-pr">
    Calculate performance ratio
    Steps:<br />
    <ol>
      <li>register job(user clicks "get started")</li>
      <li>user uploads actual performance<li>
      <li>user uploads modeled performance</li>
      <li>submit calculation</li>
      <li>Display Result</li>
    </ol>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component
export default class CalculatePR extends Vue {}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
