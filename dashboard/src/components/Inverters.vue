<template>
  <div class="Inverters">
    <div class="inverters-list">
      <h2>Inverters</h2>
      <button @click="addInverter">Add Inverter</button>
      <div class="msg warning" v-if="inverters.length == 0">
        System requires at least one inverter.
      </div>
      <ul class="inverters">
        <inverter-view
          class="inverter"
          v-for="(inverter, index) in inverters"
          :key="index"
          :index="index"
          :inverter="inverter"
          :model="model"
        />
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";
import InverterView from "@/components/Inverter.vue";
import { Inverter } from "@/types/Inverter";

Vue.component("inverter-view", InverterView);
@Component
export default class InvertersView extends Vue {
  @Prop() inverters!: Array<Inverter>;
  @Prop() model!: string;

  components = ["inverter-view"];

  addInverter() {
    this.inverters.push(new Inverter());
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
ul {
  list-style-type: none;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
}
li.inverter {
  margin: 0.5em;
  padding: 0.5em;
  border: 1px solid #000;
  width: fit-content;
}
</style>
