<template>
  <li class="array">
    <b>Name: </b><input v-model="pvarray.name" /><br />

    <b>Make and Model: </b><input v-model="pvarray.makeModel" /><br />
    <b>Inverter Name: </b> {{ $parent.$parent.inverter.name }} <br />
    <!--
    <input :parameters="pvarray.moduleParameters"/>
     -->
    <button @click="removeArray">Remove Array</button><br />
    <button @click="duplicateArray">Duplicate Array</button>
  </li>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import {
  FixedTrackingParameters,
  SingleAxisTrackingParameters
} from "@/types/Tracking";
import { PVArray } from "@/types/PVArray";

@Component
export default class ArrayView extends Vue {
  @Prop() pvarray: PVArray;
  @Prop() index: number;

  removeArray() {
    //Temporary to assert behavior works. should remove specific array.
    this.$parent.pvarrays.splice(this.index, 1);
  }
  duplicateArray() {
    this.$parent.pvarrays.push(new PVArray(this.pvarray));
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
