<template>
  <div class="arrays">
    <div class="arrays-list">
      <h2>Arrays</h2>
      <button @click="addArray">Add Array</button>
      <div class="msg warning" v-if="pvarrays.length == 0">
        System requires at least one inverter.
      </div>
      <ul>
        <array-view
          class="array"
          v-for="(pvarray, index) in pvarrays"
          :key="index"
          :index="index"
          :pvarray="pvarray"
        />
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import ArrayView from "@/components/Array";
import { PVArray } from "@/types/PVArray";

Vue.component("array-view", ArrayView);
@Component
export default class ArraysView extends Vue {
  @Prop() pvarrays: Array<PVArray>;

  addArray() {
    this.pvarrays.push(new PVArray());
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}
li.array {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
